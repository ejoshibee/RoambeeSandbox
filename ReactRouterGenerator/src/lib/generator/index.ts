import fs from 'fs-extra'
import path from 'path'
import { type TemplateType, pageTemplate } from './templates/pageTemplates.ts'
import { logger } from '../logger.ts'
import inquirer from 'inquirer'
import { detectSourceDirectory } from '../srcDirFinder.ts'
import { detectTypeScriptPreferences } from '../tsPrefFinder.ts'
import chalk from 'chalk'

interface Answers {
  pageName: string
  apiPath: string
  pageType: TemplateType
  // folderName: string
}

export const promptRouteGeneration = async (): Promise<void> => {
  const { folderName }: { folderName: string } = await inquirer.prompt([
    {
      type: 'input',
      name: 'folderName',
      message: 'Enter the name of your pages/routes folder:',
      default: 'routes',
      validate: (input: string) => /^[a-zA-Z0-9_-]+$/.test(input) || 'Folder name contains invalid characters'
    }
  ])

  const pathToFolder = path.join(process.cwd(), `src/${folderName}`)
  // check that correct folder exists under src
  if (!fs.existsSync(pathToFolder)) {
    logger.info(`Path to folder: ${pathToFolder}`)
    logger.break()
    logger.warn(`Routes folder with name ${folderName} does not exist! Run the ${chalk.cyan('init')} command or create your folder`)
    logger.break()
    // TODO: prompt user run the init command
    process.exit(1)
  }

  const answers = await inquirer.prompt(
    [{
      type: 'input',
      name: 'pageName',
      message: 'Name of the new page:',
      validate: (input: string) => input !== '' || 'Page name is required'
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
      choices: ['withLoader', 'deferredLoader', 'withParams', 'authenticatedRoute', 'lazyLoaded', 'notFound', 'layout'], // Add more types as needed
      default: 'withLoader'
    }]
  )
  const { pageName, apiPath, pageType }: Answers = answers
  logger.info(`Page Name: ${pageName}`)
  logger.info(`API Path: ${apiPath}`)
  logger.info(`Page Type: ${pageType}`)
  // logger.info(`Folder Name: ${folderName}`)
  logger.break()

  // TODO: create the page IN THE CORRECT DIRECTORY

  // sanitize the apiPath and the serviceName
  // capitalize the first char in the page name
  const sanitizedPageName = pageName[0].toUpperCase() + pageName.slice(1)

  // if present, remove the leading forward slash
  const sanitizedApiPath = apiPath[0] === '/' ? apiPath.slice(1) : `${apiPath}`

  await generatePage(sanitizedPageName, folderName, pageType, sanitizedApiPath)
}

/**
 * function to generate a page template.
 * @param {string} name The name of the service/page for the application.
 * @param {string} routeFolder The name of the route folder for the application.
 * @param {TemplateType} type The type of page to be generated (TODO: create these types)
 * @param {boolean} isTs Bool representing whether the user is using typescript or not.
 */
export const generatePage = async (name: string, routeFolder: string, type: TemplateType, apiPath: string): Promise<void> => {
  const { prefersTsx } = await detectTypeScriptPreferences()

  // create the path to the pages/routes directory
  const src = await detectSourceDirectory()
  logger.info(`src folder is: ${src}`)
  const dirPath = path.join(process.cwd(), `${src}/${routeFolder}`)

  // create a file name
  const extension = prefersTsx ? 'tsx' : 'jsx'
  const fileName = `${name}.${extension}`

  // create the path to the new file
  const filePath = path.join(dirPath, fileName)

  try {
    // check if the src/`routeFolder` page exists
    if (!fs.existsSync(dirPath)) {
      logger.error(`Routes folder with name ${routeFolder} does not exist!`)
      process.exit(0)
    }

    // check for overwriting
    if (fs.existsSync(filePath)) {
      const { overwrite }: { overwrite: boolean } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'overwrite',
          message: `The file ${fileName} already exists. Do you want to overwrite it?`,
          default: false
        }
      ])
      // if the user does not want to overwrite, log a warning and return
      if (!overwrite) {
        logger.break()
        logger.warn('Page generation cancelled.')
        return
      }
      // logger confirmation that an overwrite is happening
      // only triggered when an overwrite happens
      logger.info(`Overwriting file ${fileName}`)
    }

    // write the file to the path
    await fs.writeFile(filePath, pageTemplate(name, type, apiPath))
    logger.break()
    logger.success(`Page ${name} generated successfully.`)
  } catch (error) {
    logger.break()
    logger.error(`Error generating page ${name}:`, error)
  }
}

export const checkForTsConfig = (): boolean => {
  return fs.existsSync(path.join(process.cwd(), 'tsconfig.json'))
}
