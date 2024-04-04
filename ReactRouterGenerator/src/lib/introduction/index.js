import inquirer from 'inquirer';
import fs from 'fs';
import path from 'path';
import {parsePackageJson} from '../parsePkgJsn.js'

/**
 * the introduction command will throw the introduction to the console
 */
export const promptIntroduction = () => {
  // check if the user wants to generate routes
  inquirer.prompt([
    {
      type: 'confirm',
      name: 'generateRoutes',
      message: 'Want to generate routes?',
      default: false
    }
  ]).then(answers => {
    if (answers.generateRoutes) {
      // The user intent is to generate routes
        // need to check if their project is even setup for react-router and if it is, then we can ask the user if they want to generate routes
      // parse the package json file and store as a JSON object
      const packageJson = parsePackageJson()
        // if it is not, then we need to inform the user they are missing dependencies and ask them if they want to install them
      // check dependencies and dev dependencies for react-router
      const hasReactRouter = packageJson.dependencies['react-router'] || packageJson.devDependencies['react-router'];
      

      // Call function that defines the prompts generation
      promptRouteGeneration();
    } else {
      console.log("Route generation cancelled.");
      process.exit();
    }
  });
}

const promptRouteGeneration = async () => {
  const answers = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'hasPagesFolder',
      message: 'Do you have a pages/routes folder?',
      default: false
    },
    {
      type: 'input',
      name: 'serviceName',
      message: 'Name of the Service/Page:',
      validate: input => !!input || 'Service/Page name is required'
    },
    {
      type: 'input',
      name: 'apiPath',
      message: 'Pathname of API:',
      default: '/'
    },
    {
      type: 'list',
      name: 'pageType',
      message: 'Type of page:',
      choices: ['basic', 'other'], // Add more types as needed
      default: 'basic'
    }
  ]);

  // check answers here
  console.log(answers)
    const { hasPagesFolder, serviceName, apiPath, pageType } = answers;

    if(!hasPagesFolder) {
      console.log('\nNo Pages folder found. Will create one for you')

      const {generationType} = await inquirer.prompt([
        {
          type: 'list',
          name: 'generationType',
          message: 'Choose what to generate:',
          choices: ['routes', 'pages']
        }
      ])
      // call function to create a folder based on the generationType
      createFolder(generationType)
      console.log(`\n${generationType} folder created for you`)

    }

    // pages/routes folder has been created. Now we need to create the service/page
  }



  
const createFolder = (generationType) => {
  // need to check my working directory correct? make sure I am not in the wrong folder
  const pwd = process.cwd();
  let targetDir = pwd;

  // Check for the presence of 'src' or 'app' directory inside the working directory
  const preferredDirs = ['src', 'app'];
  for (const dir of preferredDirs) {
    if (fs.existsSync(path.join(pwd, dir))) {
      targetDir = path.join(pwd, dir);
      break;
    }
  }

  // Create a subdirectory titled (generationType) within the found directory
  const generationPath = path.join(targetDir, generationType);
  fs.mkdirSync(generationPath, { recursive: true });

  console.log(`🚀 ~ ${generationType} folder created at: ${generationPath}`);
}