# Route Generator: A CLI for React Router v6.4+

This CLI tool is designed to expedite the creation of routes and pages for React projects using React Router v6.4 and above. While still under development, it offers basic functionality to streamline your workflow.

## Roadmap (Future Development):

- **Enhanced Page Templates:** Provide a wider variety of page templates to cater to different use cases.
- **Dynamic Route Generation:** Support more complex routing scenarios and nested structures.
- **Customizable Options:** Allow users to tailor the generation process to their specific project needs.
- **Testing and Error Handling:** Implement robust testing and error handling mechanisms.
- **DONE More Informative Prompts and Validation:** For the folderName prompt, add validation to ensure the name provided doesn't include forbidden characters for file paths. For apiPath, ensure the input is a valid path format.
- **DONE Dynamic Source Directory:** Allow users to specify or auto-detect the source directory instead of hardcoding `src/${routeFolder}`, making the tool more flexible for projects with different structures.
- **Enhanced TypeScript Detection:** Extend TypeScript detection to handle JSX vs TSX and JS vs TS for projects that use JavaScript but want TSX components or vice versa.
- **DONE Confirmation Before File Creation:** Prompt the user for confirmation to overwrite an existing file before creating a new page file, preventing accidental loss of work.
- **Template Customization:** Allow users to customize or define their templates in a configuration file, making the tool adaptable to various coding styles and requirements.
- **Support for Nested Directories:** Enhance folder creation logic to support nested directories, allowing for more granular organization of files (e.g., routes/admin/users).
- **Improved Error Handling and User Feedback:** In case of errors, provide suggestions for possible fixes or links to documentation, and inform the user of the next steps or how to integrate the generated page into their application upon success.
- **Automatically Add Route to Router Configuration:** Offer to automatically update the project's router configuration with the newly created route as an advanced feature.


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


## Contribution:

Contributions are welcome! Feel free to submit issues or pull requests on the GitHub repository.

> Note: This tool is in its early stages of development. While it offers basic functionality, it may not yet cover all possible use cases.
