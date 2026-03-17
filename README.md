# Final Project Scope

# Considerations

When this project discussion was initiated, there were two potential thoughts that stemmed from another project. That project being a Course Advisor Bot which was proposed by Professor Arnold. The two thoughts that came as a result were:

1. What if a given student, with their program of study and academic history were to make modifications to their academic plan? How would the rest of their academic career look like?
2. What if a given department, were to change their course offerings? How many students would be affected and what would the outlook be?

These two-use cases prompted us to consider a “What-If” tool of some sort. The first use-case is commonly known as a **Degree-Planning**. There are various tools that have been developed or are in the process of that we felt lacked something. That something being how does the tool take into consideration a whole person’s wants, strengths, and points-of-growth. Granted that is a tall order, one is essentially trying predict a person’s behavior which impossible. So what if we scoped it down to be just to X amount of time? 

The second idea was less end-user facing and more administrative advisory. We’d be opting-in to making simulation tool for X amount of students under X kind of change. In particular, how would a department-wide course modifications impact the graduation of a given class of students? 

Both were and are good ideas; however, they’re not without equally great concerns. The former ran into the issues of privacy by accessing student academic data and authentication which in turn brings in a lot of complexity for a project of this scale. Not only that but with the Academic Plan, not everyone utilizes the tool enough for it to be an accurate source of data for prediction. An academic plan template exists for those programs that have requested it. A good number of students have no plan template and may, or may not, create one for themselves. Moreover, with the latter use-case, this task is already handled by the Associate Registrar who has specialized Workday reports in place to help faculty with analytics.

In short, we were back to square one. That is however, till we pivoted to a new need that held promise. 

## Scope

![[Ticket 174200](https://halo.calvin.edu/ticket?id=174200)](image.png)

[Ticket 174200](https://halo.calvin.edu/ticket?id=174200)

The Associate Registrar brought it to our attention that the Knowledge & Understanding section of the Core Requirements in the Academic Requirements is very complex towards students. A solution is needed that can give a student/advisor at a glance what requirements are met by virtue of their program of study (Major/Minor) and which ones aren't. 

In contrast to the aforementioned “what-if” tools, we'd be only using Academic Data, including:

- [Catalog Data](https://calvincollege-my.sharepoint.com/:x:/g/personal/mhubka_calvin_edu/IQBM1J0tNXzBSqz3rAi6WidhAQGiE7uB3Gtxk3B99adIhJY?e=uSK6Xt)—provided by Acalog's API
- Core Requirement Data

### Tools for Consideration

- Web App Functionality
    - Python-based web app (e.g. Steamlit or Django)
    - React
    - Angular
- API Resource
    - Acalog (Academic Catalog System) houses the catalog and course data for the institution. They offer a REST API for easy access of data.

### Potential Features

- [Knowledge & Understanding Calculator](https://calvincollege-my.sharepoint.com/:x:/g/personal/mhubka_calvin_edu/IQBXMnYcl_n5RbKQN4veHyfHAWz6SbfqrEYZmj8oPaCNLps?e=O2VXrI)—which helps students calculate how much of their core is left by series of checks
- AI functionality to handle changes in the Catalog
- Course Scheduler Integration
- Could potentially account for students who are carrying over from an older catalog system

## Proposed Tasks and Timeline


- March
  + Data Wrangling and Exploration
  + API Connection
  + Create Project Repository
  + Program K&U Calculator
  + Sketching out Use Cases and Web Layout
  + First Client Tests (roughly around the end of the month)
- April 
  + Final Report writing
  + Final Optimizations
  + Final Client Tests
