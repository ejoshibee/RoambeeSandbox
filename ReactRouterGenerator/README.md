# Route Generator: A CLI for React Router v6.4+

This CLI tool is designed to expedite the creation of routes and pages for React projects using React Router v6.4 and above. While still under development, it offers basic functionality to streamline your workflow.

## Features

*   **Route and Page Generation:** Generates basic route and page structures, saving you time and effort. 
*   **Interactive Prompts:** Guides you through the process with clear and informative prompts.
*   **Package.json Awareness:** Checks for the presence of `react-router-dom` to ensure compatibility.
*   **Folder Creation:** Automatically creates missing `pages` or `routes` folders based on your project structure and preferences.

## Installation

```bash
npm install route-generator -g
```

## Usage:

- Navigate to your React project's root directory in the terminal.
- Run the following command to initiate the route generation process:

```bash
$ route-generator init
? Want to generate routes? Yes
? Do you have a pages/routes folder? No
? Choose what to generate: pages
✔ pages folder created for you

# Your pages folder and basic page structure will now be generated
```

## Roadmap (Future Development):

- **Enhanced Page Templates**: Provide a wider variety of page templates to cater to different use cases.
- **Dynamic Route Generation**: Support more complex routing scenarios and nested structures.
- **Customizable Options**: Allow users to tailor the generation process to their specific project needs.
- **Testing and Error Handling**: Implement robust testing and error handling mechanisms.

## Contribution:

Contributions are welcome! Feel free to submit issues or pull requests on the GitHub repository.

> Note: This tool is in its early stages of development. While it offers basic functionality, it may not yet cover all possible use cases.
