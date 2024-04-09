import fs from 'fs-extra'
import path from 'path'
import chalk from 'chalk'
import inquirer from 'inquirer'
import { Command } from 'commander'
import { type TemplateType, pageTemplate } from '../lib/generator/pageTemplates.ts'
import { logger } from '../lib/logger.ts'
import { detectSourceDirectory } from '../lib/srcDirFinder.ts'
import { detectTypeScriptPreferences } from '../lib/tsPrefFinder.ts'

interface Answers {
  pageName: string
  apiPath: string
  pageType: TemplateType
  experimentalGeneration: boolean
  // folderName: string
}
export const generate = new Command()
  .name('generate')
  .description('Generate a page template')
  .option('-e, --experimental', 'Enable experimental generation', false)
  .action(async (options) => {
    try {
      const opts: { experimental: boolean } = options
      console.log(`opts are: ${JSON.stringify(opts)}`)
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
        [
          {
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
          }
        ]
      )

      // extract the answers from the answers object
      const {
        pageName,
        apiPath,
        pageType
        // experimentalGeneration
      }: Answers = answers
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
      const sanitizedApiPath = apiPath[0] === '/' ? apiPath.slice(1) : apiPath

      // generate the page as normal, regardless of experimental flag being true or not
      await generatePage(sanitizedPageName, folderName, pageType, sanitizedApiPath)

      // if the experimental flag is true, lets ask for the location of the router obejct to help our traversal.
      if (opts.experimental) {
        const { routerLocation }: { routerLocation: string } = await inquirer.prompt([{
          type: 'input',
          name: 'routerLocation',
          message: `Where is your router file located? Example: ${chalk.cyan('src/main.tsx')} or ${chalk.cyan('src/routes/router.jsx')}`,
          default: 'main.tsx'
          // TODO: validate input
        }])

        // the router location input is a path name to the router file
        // we need to traverse the file and add the route to the router object using jscodeshift

        // check that the path is a valid path
        if (!fs.existsSync(path.join(process.cwd(), routerLocation))) {
          logger.error(`Router file at ${routerLocation} does not exist!`)
          logger.break()
          process.exit(0)
        }

        // if we've made it here, path is valid to the file containing a router object.
        // TODO: TRIGGER THE JSCODESHIFT transformation here to modify the router
      }
    } catch (error) {
      // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
      logger.error(`Error generating page: ${error}`)
    }
  })

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
  logger.break()
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

/**
 * Function to check if the user has a tsconfig.json file in their project.
 * @returns {boolean}
 */
export const checkForTsConfig = (): boolean => {
  return fs.existsSync(path.join(process.cwd(), 'tsconfig.json'))
}
