# Purpose
Openplate was created to solve a specific issue:
    
```
Reduce repetition of create/update tasks when making many small assets(microservices, micro-uis)
```

We wanted to change this:
![Before Process Diagram shows 1-2 weeks to "create/onboard"](project-process-before.png)

Into this:
![After Process Diagram shows 5 mins to "create/onboard"](project-process-after.png)

# Process
In order to achieve this we:
- Store our project templates in dedicated git repos
- Use them to generate assets with a single command on the CLI (openplate)

![openplate flow](openplate-flow.png)
