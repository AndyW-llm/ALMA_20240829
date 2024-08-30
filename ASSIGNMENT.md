# ALMA_20240829
* By Andy Wong

## Functional Requirements

Develop an AI application to roughly assess how a person is qualified for [an O-1A immigration visa](https://www.uscis.gov/working-in-the-united-states/temporary-workers/o-1-visa-individuals-with-extraordinary-ability-or-achievement). There are 8 criterion defined in O-1A (you can find more info about those criterion by opening [this link](https://www.uscis.gov/policy-manual/volume-2-part-m#), clicking on the Appendices and expand the section of “Appendix: Satisfying the O-1A Evidentiary Requirements”)

- Awards
- Membership
- Press
- Judging
- Original contribution
- Scholarly articles
- Critical employment
- High remuneration

This rough assessment is usually done using a person’s CV and the expectation is to produce two things, 

- List all the things that the person has done and meet the 8 criterion of O-1A
- Give a rating (low, medium & high) on the chance that this person is qualified for an O-1A immigration visa

## Tech Requirements

- [x] Create a system design to fulfill the above requirements
- [x] Implement an API that takes the input of a CV as a file and produces the two things described above
- [x] Use FastAPI to implement the endpoint

## Submission Guidance

- [x] Submit your code to a publicly available github repo
- [x] Submit a [document](README.md) on why/how you make design choices and how to evaluate the output in the same repo
- [x] Any [additional documents](README.md) that could help us understand the application better in the same repo
- [x] Send an email to [shuo@tryalma.ai](mailto:shuo@tryalma.ai) with the github link within 24 hours since you start the exercise
