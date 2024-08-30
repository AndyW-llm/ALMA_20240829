import os
import copy
import json
import operator
import collections
from typing import Annotated, TypedDict, List, Dict, List, Type, Literal, Any

from langgraph.constants import Send
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from O1A_assessment.utils.llm_configs import LLM_API_dict
from O1A_assessment.utils.get_O1A_knowledge import O1A_DFFINITIONS
from O1A_assessment.utils.preprocess_resume_pdf import pdf_to_text_ver_basic

# =============== LLM Config ===============
llm_name = "gpt-4o-mini"
params = {
    "model": llm_name,
    "temperature": 0.0,
    "timeout": 500,
    "max_retries": 5,
    "api_key": LLM_API_dict[llm_name]["api_key"],
    "base_url": LLM_API_dict[llm_name]["base_url"],
}
llm = ChatOpenAI(**params)

# =============== Prompt Config ===============
# [STAGE 1] Generic Prompts for `List all the things that the person has done and meet the 8 criterion of O-1A``
prompt_extract_info = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI assistant tasked with reviewing the user's resume"\
         " to extract relevant information that could support an O-1A visa application."\
         " Please provide relevant details, such as date, location, company, journal, and conference."\
         " If no relevant information were available, return an empty list."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

criterion_template_life_long_achievements = "{brief_definition}\n"\
  "A qualified achievement must fullfill the following consideration:\n"\
  "{considerations}"\
  "Examples of a qualifed achievement:\n"\
  "{examples}"

class structured_output_life_long_achievements(BaseModel):
    """List all life long acheivements that satisfy each of the following criterion."""
    Awards: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Awards"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Awards"]["considerations"],
            examples = O1A_DFFINITIONS["Awards"]["examples"],
      )+"\nPlease provide all relevant details, such as date, school information."
    )
    Membership: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Membership"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Membership"]["considerations"],
            examples = O1A_DFFINITIONS["Membership"]["examples"],
      )+"\nPlease provide all relevant details, such as year, organization information."
    )
    Press: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Press"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Press"]["considerations"],
            examples = O1A_DFFINITIONS["Press"]["examples"],
      )+"\nPlease provide all relevant details, such as publication type, source, and date."
    )
    Judging: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Judging"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Judging"]["considerations"],
            examples = O1A_DFFINITIONS["Judging"]["examples"],
      )+"\nPlease provide all relevant details, such as conference, and date."
    )
    Original_contribution: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Original_contribution"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Original_contribution"]["considerations"],
            examples = O1A_DFFINITIONS["Original_contribution"]["examples"],
      )+"\nPlease provide all relevant details, such as journal, conference, and date."
    )
    Scholarly_articles: List[str] = Field(
        description=criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS["Scholarly_articles"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Scholarly_articles"]["considerations"],
            examples = O1A_DFFINITIONS["Scholarly_articles"]["examples"],
      )+"\nPlease provide all relevant details, such as journal, conference, and date."
    )

list_life_long_achievements_chain = prompt_extract_info | llm.with_structured_output(structured_output_life_long_achievements, include_raw=False)

# TODO: "High remuneration" does not fit well in this template
criterion_template_employment = "{brief_definition}\n"\
  "A qualified cuurent job must fullfill the following consideration:\n"\
  "{considerations}"\
  "Examples of a qualifed current job:\n"\
  "{examples}"

class structured_output_employment_status(BaseModel):
    """List information of the user's current employment that could support an O-1A visa application."""
    Critical_employment: List[str] = Field(
        description=criterion_template_employment.format(
            brief_definition = O1A_DFFINITIONS[ "Critical_employment"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["Critical_employment"]["considerations"],
            examples = O1A_DFFINITIONS["Critical_employment"]["examples"],
      )+"\nPlease provide all relevant details, such as postion and date."
    )
    High_remuneration: List[str] = Field(
        description=criterion_template_employment.format(
            brief_definition = O1A_DFFINITIONS["High_remuneration"]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS["High_remuneration"]["considerations"],
            examples = O1A_DFFINITIONS["High_remuneration"]["examples"],
      )+"\nPlease provide all relevant details, such as slary and date."
    )

employment_status_chain = prompt_extract_info | llm.with_structured_output(structured_output_employment_status, include_raw=False)

# [STAGE 2] Role play a judge, output "Pass", "Reject", "More information needed"

# NOTE: criterion_description is formulated differently (life achievement vs. employment)
criteria_map = {
    "life-long-achievements":["Awards", "Membership", "Press", "Judging", "Original_contribution", "Scholarly_articles"],
    "employment-status":["Critical_employment", "High_remuneration"],
}

prompt_judge_info = ChatPromptTemplate.from_messages(
    [
        ("system", "Please act as an impartial judge and assess whether the user's achievement meets the criterion specified below:\n"\
         "{criterion_description}"\
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
class structured_judgement(BaseModel):
    explanation: str = Field(
        description="Please explain step by step on why the user provided information meet or failed to meet the specified criterion",
    )
    verdict: str = Field(
        description="Your final judgement here, return 'Pass', 'Reject', or 'More information needed'",
    )

# [STAGE 3] Rewrite judgement (Done manually with summarize_judgement_node)

# =============== Graph State Config ===============
class CriterionState(TypedDict):
    content: str
    content_meta: str
    criterion_of_interests: str
    extracted_content: str
    extracted_contents: list[str]
    judgement: str
    judgements: list[str]
    judgement_summary: str

def create_base_state(
        content: str = "",
        content_meta: str = "",
        criterion_of_interests: str = "",
        extracted_content: str = "",
        extracted_contents: list[Any] = [],
        judgement: str="",
        judgements: list[Any] = [],
        judgement_summary: str = "",
        ) -> CriterionState:
    return CriterionState(
        content=content,
        content_meta=content_meta,
        criterion_of_interests=criterion_of_interests,
        extracted_content=extracted_content,
        extracted_contents=extracted_contents,
        judgement=judgement,
        judgements=judgements,
        judgement_summary=judgement_summary,
    )

class OverallGraphState(TypedDict):
    resume_path: str
    contents: List[Any]
    contents_meta: List[Any]
    criteria_of_interests: List[Any]
    collected_criterion_state: Annotated[list, operator.add]
    extracted_content_dict: Dict[Any, Any]
    judgement_dict: Dict[Any, Any]
    judgement_summary_dict: Dict[Any, Any]
    final_summary: str

def create_overall_state(
        resume_path: str = "",
        contents: List[Any]=[],
        contents_meta: List[Any]=[],
        criteria_of_interests: List[Any]=[],
        collected_criterion_state: Annotated[list, operator.add]=[],
        extracted_content_dict: Dict[Any, Any]={},
        judgement_dict: Dict[Any, Any]={},
        judgement_summary_dict: Dict[Any, Any]={},
        final_summary: str="",
        ) -> OverallGraphState:
    return OverallGraphState(
        resume_path=resume_path,
        contents=contents,
        contents_meta=contents_meta,
        criteria_of_interests=criteria_of_interests,
        collected_criterion_state=collected_criterion_state,
        extracted_content_dict=extracted_content_dict,
        judgement_dict=judgement_dict,
        judgement_summary_dict=judgement_summary_dict,
        final_summary=final_summary,
    )

# =============== Graph Edge Config ===============

def content_extraction_node(state: OverallGraphState):
    contents = state['contents']
    assert len(contents)==1 # NOTE: support text mode only for now.
    content_input = json.dumps({"user resume": contents[0]}, ensure_ascii=False)
    user_input = HumanMessage(content=content_input)
    response = list_life_long_achievements_chain.invoke({"messages": [user_input]})
    extracted_content_dict = copy.deepcopy(dict(response))
    response = employment_status_chain.invoke({"messages": [user_input]})
    for key, val in dict(response).items():
        extracted_content_dict[key] = val
    output = create_overall_state(
        contents=state['contents'],
        extracted_content_dict=extracted_content_dict,
    )
    return output


def distribute_judgement_cases(state: OverallGraphState):
    tasks = []
    for criterion_of_interests, extracted_contents in state['extracted_content_dict'].items():
        for extracted_content in extracted_contents:
            package = create_base_state(
                criterion_of_interests=criterion_of_interests,
                extracted_content=extracted_content,
            )
            tasks.append(Send("judge_content", package))
    return tasks


def judge_content_node(state: CriterionState):
    criterion_of_interests = state["criterion_of_interests"]
    extracted_content = state["extracted_content"]
    content_input = json.dumps({"user content": extracted_content}, ensure_ascii=False)
    user_input = HumanMessage(content=content_input)
    if criterion_of_interests in criteria_map["life-long-achievements"]:
        criterion_description = criterion_template_life_long_achievements.format(
            brief_definition = O1A_DFFINITIONS[criterion_of_interests]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS[criterion_of_interests]["considerations"],
            examples = O1A_DFFINITIONS[criterion_of_interests]["examples"],
        )
    elif criterion_of_interests in criteria_map["employment-status"]:
        criterion_description = criterion_template_employment.format(
            brief_definition = O1A_DFFINITIONS[criterion_of_interests]["evidentiary criterion"],
            considerations = O1A_DFFINITIONS[criterion_of_interests]["considerations"],
            examples = O1A_DFFINITIONS[criterion_of_interests]["examples"],
        )
    else:
        raise ValueError(f"[judge_content_node] unexpected criterion: {criterion_of_interests}")
    judgement_prompt = prompt_judge_info.partial(criterion_description=criterion_description) 
    judge_chain =judgement_prompt | llm.with_structured_output(structured_judgement, include_raw=False)
    response = judge_chain.invoke({"messages": [user_input]})
    output = create_base_state(
        criterion_of_interests = state["criterion_of_interests"],
        extracted_content = state["extracted_content"],
        judgement = dict(response)
        
    )
    return {"collected_criterion_state": [output]}


def collect_judgement_node(state: OverallGraphState):
    judgement_dict = collections.defaultdict(list)
    for i, j in enumerate(state['collected_criterion_state']):
        criterion_of_interests = j['criterion_of_interests']
        reformat_judgement = {
            "extracted_content": j['extracted_content'],
            "verdict": j['judgement']['verdict'],
            "rationale": j['judgement']['explanation'].replace('\\n', '\n'),
        }
        judgement_dict[criterion_of_interests].append(reformat_judgement)

    return create_overall_state(
        contents=state['contents'],
        extracted_content_dict=state['extracted_content_dict'],
        judgement_dict=judgement_dict,
    )


def summarize_judgement_node(state: OverallGraphState):
    criteria = ["Awards", "Membership", "Press", "Judging", "Original_contribution", "Scholarly_articles", "Critical_employment", "High_remuneration"]
    judgement_summary_dict = {
        "Content Passed": {criterion:0 for criterion in criteria}, 
        "Content needed more information":{criterion:0 for criterion in criteria}, 
        "Rating":"N/A",
        "Rating rationale":"N/A",
    }
    for criterion_of_interests, reformat_judgements in state['judgement_dict'].items():
        for reformat_judgement in reformat_judgements:
            if reformat_judgement["verdict"].lower()=="pass":
                judgement_summary_dict["Content Passed"][criterion_of_interests]+=1
            elif reformat_judgement["verdict"].lower()=="more information needed":
                judgement_summary_dict["Content needed more information"][criterion_of_interests]+=1

    # NOTE: The rating will be based on the following conditions:
    # High: Three criteria have been identified, with high confidence that the requirements for those criteria have been fully met.
    # Medium: Three potential criteria have been identified (including at least one with high confidence), but additional information or justification is needed to ensure the requirements are fully satisfied.
    # Low: Any other cases that do not meet the above conditions.
    solid_criteria = [criterion for criterion, count in judgement_summary_dict["Content Passed"].items() if count >= 1]
    questionable_criteria = [criterion for criterion, count in judgement_summary_dict["Content needed more information"].items() if (count >= 1) and (criterion not in solid_criteria)]
    
    if len(solid_criteria)>=3:
        judgement_summary_dict["Rating"] = "High"
        judgement_summary_dict["Rating rationale"] = f"The user's experience will likely satisfy {len(solid_criteria)} criteria {solid_criteria} for O-1A application."
        if questionable_criteria>=1:
            judgement_summary_dict["Rating rationale"]+=f"\nAdditional experience in {len(questionable_criteria)} criteria {questionable_criteria} could potentially satisfy O-1A requirement."
    elif len(solid_criteria)+len(questionable_criteria)>=3 and len(solid_criteria)>=1:
        judgement_summary_dict["Rating"] = "Medium"
        judgement_summary_dict["Rating rationale"] = f"The user's experience will likely satisfy {len(solid_criteria)} criteria {solid_criteria} for O-1A application."
        judgement_summary_dict["Rating rationale"]+=f"\nMore information is needed in {len(questionable_criteria)} criteria {questionable_criteria} to see if O-1A requirements could be met."
    else:
        judgement_summary_dict["Rating"] = "Low"
        judgement_summary_dict["Rating rationale"] = f"The user's experience will likely satisfy {len(solid_criteria)} criteria {solid_criteria} for O-1A application."
        judgement_summary_dict["Rating rationale"]+=f"\nMore information is needed in {len(questionable_criteria)} criteria {questionable_criteria} to see if O-1A requirements could be met."
        judgement_summary_dict["Rating rationale"]+=f"\nPlease review the O-1A criteria and revise the resume to include more experices or details about your current/future employment status."
    
    formatted_contents = ""
    count_i = 0
    for criterion_of_interests, reformat_judgements in state['judgement_dict'].items():
        count_i+=1
        count_j = 0
        formatted_contents += f"\n\n{count_i}.  {criterion_of_interests}:"
        for reformat_judgement in reformat_judgements:
            if reformat_judgement['verdict'].lower()=="reject":
                continue
            count_j+=1
            formatted_contents += f"\n\n  {count_i}.{count_j} {reformat_judgement['extracted_content']}:"
            rationale_indent = '       '+reformat_judgement['rationale'].replace('\n','\n       ')
            formatted_contents += f"\n    •  [{reformat_judgement['verdict']}]\n{rationale_indent}"

    final_summary = [
        "\n\nList all the things that the person has done and meet the 8 criterion of O-1A:", 
        formatted_contents,
        f"\n\nRating: {judgement_summary_dict['Rating']}",
        judgement_summary_dict["Rating rationale"],
    ]
    final_summary = "\n".join(final_summary)

    return create_overall_state(
        contents=state['contents'],
        extracted_content_dict=state['extracted_content_dict'],
        judgement_dict=state['judgement_dict'],
        judgement_summary_dict=judgement_summary_dict,
        final_summary = final_summary,
    )

# =============== Graph Config ===============
workflow = StateGraph(OverallGraphState)
workflow.add_node("content_extraction", content_extraction_node)
workflow.add_node("judge_content", judge_content_node)
workflow.add_node("collect_judgement", collect_judgement_node)
workflow.add_node("summarize_judgement", summarize_judgement_node)

workflow.set_entry_point("content_extraction")
workflow.add_conditional_edges("content_extraction", distribute_judgement_cases) # send to: judge_content
workflow.add_edge("judge_content", "collect_judgement")
workflow.add_edge("collect_judgement","summarize_judgement")

graph = workflow.compile()

# =============== workflow wrapper ===============
# Execute single case
def basline_fn(input_file_path, output_dir):
    # =============== Preprocess input ===============
    pdf_text = pdf_to_text_ver_basic(pdf_path = input_file_path)
    contents = [pdf_text]

    # =============== INFERENCE ===============
    initial_state = create_overall_state(
        contents = contents,
    )
    result = graph.invoke(initial_state)

    # =============== EXPORT to local ===============
    os.makedirs(output_dir, exist_ok=True)
    export_path = os.path.join(output_dir, "workflows_output.jsonl")
    with open(export_path, 'w', encoding='utf-8') as file:
        entry = {
            "workflow": "baseline",
            "contents": contents,
            "extracted_content_dict": result["extracted_content_dict"],
            "judgement_dict": result["judgement_dict"],
            "judgement_summary_dict":result["judgement_summary_dict"],
            "final_summary":result["final_summary"],
        }
        json_line = json.dumps(entry, ensure_ascii=False)
        file.write(json_line + '\n')
        file.flush()

    # =============== RETURN OUTPUT to user ===============
    print(f"Export completed to {export_path}")
    formatted_result = {
        "content": result["final_summary"],
    }
    return formatted_result