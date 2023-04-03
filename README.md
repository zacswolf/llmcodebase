# About

The goal of this project is to interface LLM with any codebase so that developers can ask various questions on it.

## Possible developer questions -> tools

- What is the purpose of this function? - Source code, Documentation systems

- What are the inputs and outputs of this function? - Source code, Documentation systems

- Can you show me examples of how to use this function? - Source code, Documentation systems

- Are there any known issues or bugs in this function? - Issue tracking systems

- What are the dependencies for this function or module? - Source code, Build systems, Dependency and package managers

- How is this function being tested? - Source code, Testing frameworks and tools

- Are there any performance bottlenecks in this code? - Source code, Performance profiling tools

- What are the best practices followed in this codebase? - Source code, Code analysis and linting tools

- How is error handling implemented in this function or module? - Source code

- Are there any security vulnerabilities in this code? - Source code, Security scanning tools, Vulnerability databases

- How can I refactor this code to make it more efficient or readable? - Source code, Code analysis and linting tools

- What coding style or conventions are followed in this codebase? - Source code, Code analysis and linting tools

- Can you find all instances where this function is called? - Source code, Integrated Development Environments (IDEs)

- How does this class or module interact with other classes or modules? - Source code

- What are the key architectural decisions made in this codebase? - Source code, Documentation systems

- Are there any deprecated functions or libraries used in this code? - Source code, Dependency and package managers

- How is data validation and sanitization done in this code? - Source code

- Can you show me the commit history of this file or function? - Version control systems

- What are the most frequently modified parts of this codebase? - Version control systems

- Are there any code comments or documentation that provide more context? - Source code, Documentation systems

- Can you provide an overview of the project structure? - Source code

- How are the different components or modules of the project organized? - Source code

- What is the main entry point of the application? - Source code

- Can you generate a dependency graph for the entire project? - Source code, Build systems, Dependency and package managers

- What are the key design patterns used in this codebase? - Source code

- How is the project configured, and what are the important configuration files? - Build systems, Configuration files

- What third-party libraries or frameworks are used in this project, and what are their versions? - Dependency and package managers

- How is the build process set up for this project, and what build tools are used? - Build systems

- Are there any performance or resource usage metrics available for the application? - Performance profiling and monitoring tools

- How is the project tested, and what testing frameworks or methodologies are used? - Testing frameworks and tools

- Are there any continuous integration and deployment (CI/CD) pipelines set up for this project? - Continuous Integration and Deployment (CI/CD) systems

- What coding standards or style guides are followed across the codebase? - Code analysis and linting tools

- Can you show me the overall commit history and trends for the entire project? - Version control systems

- Who are the main contributors to this project, and what parts of the codebase have they worked on? - Version control systems

- Are there any outstanding issues, bugs, or feature requests for the project? - Issue tracking systems

- How is the project versioned, and what is the release history? - Version control systems, Build systems

- Can you identify any code that is not being used or is deprecated? - Source code, Code analysis and linting tools

- Are there any known security vulnerabilities in the project? - Security scanning tools, Vulnerability databases

- How is logging and monitoring implemented across the application? - Source code, Performance profiling and monitoring tools

- Can you provide an overview of the project's documentation? - Documentation systems

## Start with focusing on a source code understanding tool.

## It would be amazing to be able to answer the following questions:

- How does the implementation of the caching mechanism in this codebase work?

- Can you summarize the main responsibilities of the OrderProcessor class?

- Which functions in the codebase are most similar to the calculate_tax function in terms of functionality?

- Are there any instances where the Single Responsibility Principle is violated in this codebase?

- What are the most commonly used design patterns in this codebase, and where are they implemented?

- How does the error handling in this project compare to best practices for this programming language?

- What is the relationship between the User class and the Authentication module?

- How is the project's database schema designed, and how does the code interact with it?

- How does this codebase handle concurrency and parallelism?

- How does the codebase handle internationalization and localization?

- Can you provide a high-level overview of the data flow in this codebase?

## To run

Note: you will have to change the timestamps on the json and msgpack files. Also python 3.11 or newer is required.

```
mkdir codebases
mkdir outputs
cd codebases
git clone git@github.com:hwchase17/langchain.git
cd ..
python crawl.py --root_path codebases/langchain  -P "codebases/langchain" -P "codebases/langchain/langchain*"
python embedding_generator.py --info_path outputs/03_22_21_30_12.json
python question_intaker.py -p outputs/03_22_12_29_32.msgpack -q "What are the supported parsers?"
python -m uvicorn app:app --reload
```
