# ALMA_20240829
Prepared by Andy Wong

## Shortcuts
- [O-1A Qualification Assessment Workflow](#O-1A-Qualification-Assessment-Workflow).
- [Design Choices: Rationale and Implementation](#Design-Choices:-Rationale-and-Implementation).
- [Additional Thoughts](#Additional-Thoughts).
- [How to evaluate the output?](#How-to-evaluate-the-output?).
- [Instruction](#Instruction).

## Product Objective
The objective of the product is to provide an AI-driven tool capable of analyzing a candidate's CV and delivering a structured, criterion-based assessment of their qualifications. The output should be actionable, offering clear insights into the candidate's strengths and identifying areas where additional evidence or information may be required.

## Business Objective
The primary business objectives are:
  - **Boost Customer Acquisition and Conversion:**<br/>
  By offering this product as a free trial service, we aim to reach a broader audience, enhancing customer outreach and improving the conversion rate of potential customers into subscribers of our paid service.
  - **Enhance Producitvity for Professionals:**<br/>
  Streamline the review process for immigration attorneys, allowing them to work more efficiently and focus their expertise on more complex tasks.

## O-1A Qualification Assessment Workflow
### Input: 
  - A candidate's CV in PDF format.
### Outputs:
  - A detailed list of accomplishments and current job positions aligned with each of the eight USCIS criteria: Awards, Membership, Press, Judging, Original Contribution, Scholarly Articles, Critical Employment, and High Remuneration.
  - For each accomplishment or job position, provide a rationale explaining why it may satisfy USCIS's criteria or why additional information is needed.
  - An overall application rating (Low, Medium, High).
    - *High*: Three criteria have been identified, with high confidence that the requirements for those criteria have been fully met.
    - *Medium*: Three potential criteria have been identified (including at least one with high confidence), but additional information or justification is needed to ensure the requirements are fully satisfied.
    - *Low*: Any other cases that do not meet the above conditions.
  - Brief, actionable insights identifying the criteria where the candidate's strengths are evident and areas where further evidence may be required.
### Key Components and Workflow:
  - **[Example of Calling the FastAPI Service](O1A_assessment/api_call_example.py)**: 
    - Upload a local PDF file to the API.
    - Print the final outputs from the API.

  - **[Initialize FastAPI Service](O1A_assessment/api_ver_fast_api.py)**: 
    - Handle user requests.
    - Execute the workflow.
    - Send the final output back to the user.

  - **[Route Workflows](O1A_assessment/inference/workflows.py)**: 
    - Currently, only the `baseline` (Default) workflow is supported.

  - **[Baseline Workflow Implementation](O1A_assessment/inference/baseline.py)**: 
    - **Preprocess Input (PDF) into Text**:
      - Convert the PDF into text for further processing.
    
    - **Execute Workflow / LLM Inference**:
      - **LLM**: "gpt-4o-mini"
      - **Stage 1**: Extract information from the resume.
        - Single inference call.
        - Provide the LLM with a criterion description (tool calling description) and resume text (user prompt).
        - Return a structured output of relevant information that could potentially support each criterion of an O-1A visa application.
      - **Stage 2**: Judge whether each piece of information meets its corresponding criterion.
        - Multiple inference calls (n = number of pieces of information extracted in Stage 1).
        - Provide the LLM with a criterion description (system prompt) and a single piece of information (user prompt).
        - Return structured outputs of "explanation" and "verdict" ('Pass', 'Reject', or 'More information needed').
      - **Stage 3**: Post-process LLM Outputs.
        - Assign a rating based on predefined conditions.
        - Reformat intermediate and final outputs.

    - **Export Intermediate and Final Outputs for Internal Evaluation**:
      - Export data for further analysis and assessment.

    - **Return Final Output**:
      - Send the processed final output back to the user.

  - **[Evaluation](O1A_assessment/eval)**: 
    - **Work in progress**:


## Design Choices: Rationale and Implementation

### Implementation Focus
The application is designed with scalability and future improvements in mind. The architecture supports the easy integration of criterion-specific workflows, allowing the system to adapt to updated criteria and evolving requirements. This forward-thinking approach ensures that the application remains flexible and robust, enabling seamless enhancements without overhauling the entire system. For more details, see the [Potential Improvements](#potential-improvement) section.

### PDF to Text
In choosing the PDF to text conversion tool, I opted for `PyMuPDFReader` wrapped under `lama_index.readers.file` to quickly prototype the implementation. While more sophisticated and reliable tools like [Marker](https://github.com/VikParuchuri/marker) and [LlamaParse](https://docs.llamaindex.ai/en/stable/llama_cloud/llama_parse/) are available, this choice was driven by the need for rapid development. The current implementation allows for quick validation of the concept while leaving room for future upgrades to more robust solutions as the project evolves.

### Model Selection
The selection of the LLM model, "gpt-4o-mini," was guided by a balance between cost and performance. It is one of the most affordable yet powerful models available, which reduces the cost of both experimentation and deployment. This model also provides the possibility for fine-tuning, enabling a more tailored solution as needed. Additionally, its structured output functionality facilitates the design of intricate "agentic" workflows, making it a cost-effective choice for developing a sophisticated and scalable application.

### Structured Output
Structured output from the LLM is crucial for this application. It simplifies development by ensuring a consistent format that can be easily processed in subsequent stages. This approach allows for seamless integration between the LLM output and the programmed functions (e.g., Stage 3 post-processing), ensuring that the workflow remains efficient and reliable.

### Problem Decomposition
The assessment process is designed to evaluate each accomplishment and current job position independently. This method allows for more precise control over the workflow, especially when using smaller LLM models. By decomposing the problem into manageable components, the application can deliver better responses and maintain flexibility in handling complex cases.

### Assumptions
- **User Submission**: The user submits a CV in PDF format.
- **Residency Status**: The user does not have U.S. permanent residency (Green Card) or citizenship.
- **Purpose**: The user seeks a preliminary assessment of their eligibility for the O-1A visa.
- **Accuracy of CV**: The CV provided is factually accurate and includes all necessary information to evaluate O-1A eligibility (e.g., the rarity of achievements in their field).
  - **Note**: The "High Remuneration" criterion may be challenging to evaluate if salary information is not included in the CV.
- **Award Status**: The user has not received a major internationally recognized award (e.g., Nobel Prize). Such cases typically do not require a preliminary assessment.
  - **Note**: If required by business needs, a specialized evaluation process for awards can be developed.

### Problem Boundaries
- **Focus Area**: Due to limited data availability (e.g., descriptions from the USCIS website) and time constraints, this application primarily focuses on assessing eligibility for the O-1A visa within the STEM (Science, Technology, Engineering, Mathematics) fields.
- **Other Fields**: The user may also be eligible for the O-1A visa in other fields (e.g., Education, Business, Athletics). These cases might require domain-specific prompts and examples, which are beyond the current scope.
- **Edge Cases**: Scenarios involving "continued work in the area of extraordinary ability" are outside the scope of this application.

## Additional Thoughts

### Known Issues

- **Data Collection**: 
  - Currently, there is a lack of real-world resume samples and corresponding labels, which are essential for training and evaluating the application effectively. A potential source for qualified O-1A examples could be resumes from university professors, who often meet the visa's stringent criteria. For unqualified examples, one could scrape publicly available resumes from LinkedIn or other self-hosted free services. These would then need to be manually evaluated by expert attorneys to ensure accuracy and relevance.

- **Evaluation**: 
  - The evaluation pipeline is still under development, with current efforts focused on processing a single resume. This approach limits the ability to perform aggregation of metrics and macro-scale analysis. Expanding the evaluation to handle multiple resumes simultaneously will be crucial for assessing the application's overall effectiveness and reliability across different cases.

- **Awards**: 
  - University awards play a significant role in the O-1A visa evaluation process. Therefore, these awards should be explicitly matched against [R1 or R2 doctoral universities](/knowledges/definitions.json) to assess their merit accurately. The current implementation relies on the LLM's parametric memory, which may not always provide the necessary precision. A more robust approach would involve direct validation against a verified list of recognized institutions.

- **Press**: 
  - Evaluating qualifications related to press coverage requires additional documentation, such as copies of news articles or media mentions. Without this supplementary information, it is challenging to assess the credibility and significance of the press coverage accurately.

- **High Remuneration**: 
  - Evaluating the "High Remuneration" criterion is problematic due to the likely absence of salary information in the CV. This issue limits the application's ability to assess this criterion reliably. Future iterations should explore integrating external data sources to supplement this information.

### Potential Improvements

- **In-Context Learning**: 
  - Providing the LLM with verified pairs of input and output can enhance the accuracy of intermediate results. However, this comes at the cost of additional token usage, which may increase overall processing costs. The trade-off between improved accuracy and increased cost needs careful consideration.

- **Retrieval-Augmented Generation (RAG)**: 
  - Implementing RAG could enable the application to retrieve contextually similar examples from a larger dataset, thereby enhancing the effectiveness of in-context learning. This approach could lead to more accurate assessments, especially in complex cases where nuanced understanding is required.

- **Remove Dependency on LangChain/LangGraph**: 
  - The current workflow is implemented using LangChain and LangGraph due to time constraints. For future adaptability, particularly in cases requiring highly customized workflows or evaluations with large collections of examples, it would be beneficial to build the workflow from scratch using only the OpenAI API. This approach would also enable batch inference, potentially reducing the cost of OpenAI API usage by half.

- **Tool Calling**: 
  - Incorporating tool calling can help gather updated auxiliary information, improving the accuracy of certain assessments:
    - **High Remuneration**: Integrating salary and wage databases from sources like [The Bureau of Labor Statistics (BLS) Overview of BLS Wage Data by Area and Occupation webpage](https://www.bls.gov/bls/blswage.htm) and [The Department of Labor's Career One Stop webpage](https://www.careeronestop.org/ExploreCareers/Plan/salaries.aspx) would provide the necessary data to assess this criterion more accurately.

- **Problem Decomposition in Stage 1**:
  - Additional work could improve the `content extraction` step. The current single inference call approach might miss critical information, leading to inaccuracies in later stages of the assessment. Although evaluating and modifying prompts could mitigate this, the root cause lies in the complexity of the content extraction task. Decomposing the content extraction by each criterion (similar to the Stage 2 `judge_content` step) could significantly enhance stability.
  - To further minimize the risk of missing crucial information, the CV could be processed in two formats: as text and as image screenshots. This dual approach enhances assessment accuracy. 
  - Processing the resume one page at a time could also prevent the loss of information, a phenomenon known as "Lost in the Middle." While this method may be more resource-intensive, it is expected to yield more reliable results. 
  Future work should compare these approach against simpler implementations, evaluating them based on metrics such as reliability, cost, and latency.


## How to evaluate the output?
### sucess in retreival 
###  accuracy/precision/recall in ratings
### cost (in terms of tokens)
###  latency/throughput
###  Additional consideration: 
  - balanced dataset (should collect a variety of failed cases, especially those near the decision boundary)


## Instruction

## #installation
#### Create a conda environment with `Python 3.10`:
``` bash
  conda create --name ALMA python=3.10
  conda activate ALMA
```
#### Install `ALMA` package
```bash
  git clone https://github.com/AndyW-llm/ALMA_20240829
  cd ALMA_20240829
  pip install -e .
```
#### Store your `OPEN AI API ` key:
```bash
  cd ALMA_20240829
  cp "./secrets_template.env" "./secrets.env"
```
Manually modify `./secrets.env` to export `YOUR_KEY` for variable `OAI_API_KEY`.

### launch API service
```bash
  cd ALMA_20240829
  conda activate ALMA
  python ./O1A_assessment/api_ver_fast_api.py --host "0.0.0.0" --port 8000 --output_dir "./results" --workflow_version default
```

### API usage examples
```bash
  cd ALMA_20240829
  conda activate ALMA
  python ./O1A_assessment/api_call_example.py --input_resume_path /local/path/to/your/resume.pdf --url http://host_url/process
```
For example, `python ./O1A_assessment/api_call_example.py --input_resume_path ./examples/20240804_AndyWong_Resume.pdf --url http://localhost:8000/process` will yield the following output.
```
Parsed Arguments:
   input_resume_path: ./examples/20240804_AndyWong_Resume.pdf
   url: http://localhost:8000/process


List all the things that the person has done and meet the 8 criterion of O-1A:


1.  Awards:

  1.1 Henry A. Jastro Research Award, UC Davis, 2021:
    •  [More information needed]
       1. The Henry A. Jastro Research Award is associated with UC Davis, which is a well-known national institution.  
       2. The award is likely given for research excellence, which aligns with the criterion of recognizing achievements in a field of endeavor.  
       3. However, the information provided does not specify whether the award has national or international significance, nor does it detail the criteria for granting the award or the number of recipients.  
       4. Without additional context on the recognition level of the award and its competitiveness, it is difficult to fully assess its qualification under the specified criterion.  
       5. Therefore, while the award is from a reputable institution, more information is needed to determine if it meets the national or international recognition requirement.

  1.2 SPUR Research award, UC Berkeley, 2015:
    •  [More information needed]
       1. The SPUR Research award is associated with UC Berkeley, which is a well-known R1 doctoral university, indicating a level of national recognition.  
       2. The award is likely to have specific criteria for selection, which may include excellence in research, but further details on the criteria are needed to fully assess its significance.  
       3. The national significance of the award can be inferred from the reputation of UC Berkeley, but it is important to confirm whether the award is recognized beyond the university level.  
       4. The number of awardees and the limitations on eligible competitors are not provided, which makes it difficult to assess the competitiveness of the award.  
       5. Overall, while the SPUR Research award has potential merit due to its association with a prestigious institution, more information is needed regarding its national or international recognition and the criteria for selection to determine if it meets the specified criterion for excellence in the field.

2.  Original_contribution:

  2.1 Multiscale Assessment of Agricultural Consumptive Water Use in California’s Central Valley, Water Resources Research, Vol. 57, Issue 9, 2021:
    •  [More information needed]
       The user has provided a publication titled 'Multiscale Assessment of Agricultural Consumptive Water Use in California’s Central Valley' in a reputable journal, 'Water Resources Research'. This indicates that the work has undergone peer review, which is a strong indicator of its originality and significance. However, to assess whether this work constitutes a major contribution to the field, we need to consider additional factors such as the impact of the research on the field, whether it has provoked widespread commentary, and how often it has been cited by other researchers. The provided information does not include any evidence of citations, testimonials, or letters from experts that would further establish the significance of this work. Therefore, while the publication itself is a positive indicator, it does not alone demonstrate that the work is of major significance without additional supporting evidence.

3.  Scholarly_articles:

  3.1 Knowledge-Guided Recurrent Neural Networks for Monthly Forest Carbon Uptake Estimation, AAAI AI2ASE Workshop, 2023:
    •  [More information needed]
       1. The user has provided a title of a publication: 'Knowledge-Guided Recurrent Neural Networks for Monthly Forest Carbon Uptake Estimation'.  
       2. The publication is associated with the AAAI AI2ASE Workshop, which indicates it is a conference presentation.  
       3. The title suggests that the content is related to original research in the field of artificial intelligence and environmental science, which aligns with the definition of a scholarly article.  
       4. However, the information does not specify whether the user is a listed author of the article, which is a requirement to meet the criterion.  
       5. Additionally, there is no mention of whether the article is peer-reviewed or if it includes scholarly elements such as footnotes, endnotes, or a bibliography.  
       6. While conference presentations can be considered scholarly, the lack of clarity on authorship and peer-review status means that the evidence provided does not fully meet the specified criterion.  
       7. Therefore, more information is needed to determine if the user meets the authorship requirement and the scholarly nature of the publication.

  3.2 Multiscale Assessment of Agricultural Consumptive Water Use in California’s Central Valley, Water Resources Research, Vol. 57, Issue 9, 2021:
    •  [Pass]
       1. The user has provided a specific article title: 'Multiscale Assessment of Agricultural Consumptive Water Use in California’s Central Valley'.  
       2. The article is published in 'Water Resources Research', which is a recognized professional journal in the field of water resources and environmental studies.  
       3. The citation includes volume and issue numbers (Vol. 57, Issue 9, 2021), indicating that it is a formal publication.  
       4. The journal 'Water Resources Research' is known for publishing scholarly articles that are peer-reviewed, which aligns with the requirement for the article to be scholarly.  
       5. The user does not need to be the sole or first author to meet the criterion, and the information provided does not specify the authorship position, but it confirms that the user is a listed author.  
       6. The article likely includes elements such as footnotes, endnotes, or a bibliography, as is typical for scholarly articles, although this is not explicitly stated in the user's content.  
       7. Overall, the publication meets the criteria of being a scholarly article in a professional journal, thus fulfilling the requirement for evidence of authorship in the field.

4.  Critical_employment:

  4.1 Senior Research Scientist - Ping An, Research Lab, Palo Alto, CA (03/2021 - Present):
    •  [More information needed]
       1. **Position Title**: The user holds the title of 'Senior Research Scientist' at Ping An, which is a well-known financial services and insurance company based in China, with a research lab located in Palo Alto, CA. This suggests a level of seniority and expertise in their field.  
       
       2. **Organization's Reputation**: Ping An is recognized as one of the largest and most distinguished financial services companies globally, with a significant customer base and a strong reputation in the industry. This meets the criterion of the organization having a distinguished reputation.  
       
       3. **Critical or Essential Role**: The title of 'Senior Research Scientist' implies a leadership role, which often qualifies as critical or essential. However, to fully assess whether the user's role is critical or essential, more information is needed regarding the specific duties and contributions of the user in this position.  
       
       4. **Contribution to Organization**: The evidence provided does not detail the user's specific contributions or how their role is integral to the organization's goals or activities. Without this information, it is difficult to determine if the user's performance is significant compared to others in similar positions.  
       
       5. **Supporting Evidence**: There is no mention of detailed letters or testimonials from individuals with personal knowledge of the user's role, which would strengthen the case for the critical or essential nature of their position.  
       
       In conclusion, while the user's position at a distinguished organization suggests potential for a critical or essential role, the lack of detailed information about their specific contributions and performance means that the evidence is insufficient to fully meet the criterion. Therefore, more information is needed to make a definitive judgment.

5.  High_remuneration:

  5.1 Senior Research Scientist - Ping An, Research Lab, Palo Alto, CA (03/2021 - Present):
    •  [More information needed]
       1. The user has provided their current job title (Senior Research Scientist) and the employer (Ping An, Research Lab) along with the location (Palo Alto, CA) and the duration of employment (since March 2021).  
       2. However, the information provided does not include any evidence of the salary or remuneration for this position, such as pay statements, tax returns, or a job offer letter.  
       3. There is also no comparative wage data or evidence that the salary is high relative to others in similar occupations in the field.  
       4. Without this critical information, it is impossible to assess whether the compensation meets the criterion of being high relative to others in the same field.  
       5. Therefore, more information is needed to evaluate the user's achievement against the specified criterion.


Rating: Medium
The user's experience will likely satisfy 1 criteria ['Scholarly_articles'] for O-1A application.
More information is needed in 4 criteria ['Awards', 'Original_contribution', 'Critical_employment', 'High_remuneration'] to see if O-1A requirements could be met.
```

### Evaluate examples (In Progress)
Due to time constraint, current implementation only evaluate one resume file, for one assessment workflow at a time.
```bash
  cd ALMA_20240829
  conda activate ALMA
  python ./O1A_assessment/eval.py --src_file ./results/20240830_102923_2889f8e1-4da1-4a83-9380-7d8c8db9eb15/20240804_AndyWong_Resume.pdf
```