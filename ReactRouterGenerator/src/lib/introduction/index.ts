import inquirer from 'inquirer'
import fs from 'fs'
import path from 'path'
import { parsePackageJson } from '../parsePkgJsn.ts'
import { logger } from '../logger.ts'

/**
 * the introduction command will throw the introduction to the console
 */
export const promptIntroduction = async (): Promise<void> => {
  // check if the user wants to generate routes
  const { generateRoutes }: { generateRoutes: boolean } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'generateRoutes',
      message: 'Want to generate routes?',
      default: false
    }
  ])
  if (generateRoutes) {
    // The user intent is to generate routes
    // need to check if their project is even setup for react-router and if it is, then we can ask the user if they want to generate routes
    // parse the package json file and store as a JSON object
    const packageJson = parsePackageJson()
    logger.info('🚀 ~ promptIntroduction ~ packageJson:', packageJson)

    const dependencies = packageJson?.dependencies ?? {}
    const devDependencies = packageJson?.devDependencies ?? {}
    // check for presence of react-router in dependencies or dev-dependencies
    const hasReactRouter: boolean = Object.keys(dependencies).includes('react-router-dom') || Object.keys(devDependencies).includes('react-router-dom')

    // truthy or false value
    if (!hasReactRouter) {
      logger.error('\nReact Router is not installed. Please install it to generate routes.')
      // process.exit()
    }

    // if it is not, then we need to inform the user they are missing dependencies and ask them if they want to install them
    // check dependencies and dev dependencies for react-router

    // Call function that defines the prompts generation
    await promptRouteGeneration()
  } else {
    logger.error('Route generation cancelled.')
    process.exit()
  }
}

/**
 * Main function to prompt the user for the route generation and handle logical flow
 */
const promptRouteGeneration = async (): Promise<void> => {
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
      validate: (input: string) => input !== '' || 'Service/Page name is required'
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
  ])

  // check answers here
  logger.info(answers)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { hasPagesFolder, serviceName, apiPath, pageType } = answers

  if (hasPagesFolder === false) {
    logger.info('\nNo Pages folder found. Will create one for you')

    const { generationType }: { generationType: 'routes' | 'pages' } = await inquirer.prompt([
      {
        type: 'list',
        name: 'generationType',
        message: 'Choose what to generate:',
        choices: ['routes', 'pages']
      }
    ])
    // call function to create a folder based on the generationType
    createFolder(generationType)
    logger.success(`\n${generationType} folder created for you\n`)
  }

  // pages/routes folder has been created. Now we need to create the service/page
}

const createFolder = (generationType: string): void => {
  // need to check my working directory correct? make sure I am not in the wrong folder
  const pwd = process.cwd()
  let targetDir = pwd

  // Check for the presence of 'src' or 'app' directory inside the working directory
  // TODO: Abstract this loop away with the pwd declaration above to have a reusable sourceDirectory finder
  const preferredDirs = ['src', 'app']
  for (const dir of preferredDirs) {
    if (fs.existsSync(path.join(pwd, dir))) {
      targetDir = path.join(pwd, dir)
      break
    }
  }

  // Create a subdirectory titled (generationType) within the found directory
  const generationPath = path.join(targetDir, generationType)
  fs.mkdirSync(generationPath, { recursive: true })

  logger.success(`🚀 ~ ${generationType} folder created at: ${generationPath}`)
}
