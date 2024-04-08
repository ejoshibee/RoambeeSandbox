import inquirer from 'inquirer'
import fs from 'fs'
import path from 'path'
import { parsePackageJson } from '../parsePkgJsn.ts'
import { logger } from '../logger.ts'
import { execa } from 'execa'
import { detect } from '@antfu/ni'
import { type PackageJson } from 'type-fest'
import { detectSourceDirectory } from '../srcDirFinder.ts'

/**
 * the introduction command will throw the introduction to the console
 */
export const promptIntroduction = async (): Promise<void> => {
  // check if the user wants to generate routes
  // const { generateRoutes }: { generateRoutes: boolean } = await inquirer.prompt([
  //   {
  //     type: 'confirm',
  //     name: 'generateRoutes',
  //     message: 'Want to generate routes?',
  //     default: false
  //   }
  // ])

  // // parse the package json file and store as a JSON object
  // const packageJson = parsePackageJson()

  // // The user intent is to generate routes
  // // need to check if their project is even setup for react-router and if it is, then we can ask the user if they want to generate routes
  // if (generateRoutes) {
  //   logger.info('🚀 ~ promptIntroduction ~ packageJson:', packageJson)

  //   // check for presence of react-router in dependencies or dev-dependencies
  //   const dependencies = packageJson?.dependencies ?? {}
  //   const devDependencies = packageJson?.devDependencies ?? {}
  //   const hasReactRouter: boolean = Object.keys(dependencies).includes('react-router-dom') || Object.keys(devDependencies).includes('react-router-dom')

  //   // if no react-router, then we need to inform the user they are missing dependencies and ask them if they want to install them
  //   if (!hasReactRouter) {
  //     logger.break()
  //     logger.error('React Router is not installed. ')
  //     logger.break()

  //     const { installReactRouter }: { installReactRouter: boolean } = await inquirer.prompt([
  //       {
  //         type: 'confirm',
  //         name: 'installReactRouter',
  //         message: 'Do you want to install react-router-dom?',
  //         default: false
  //       }
  //     ])
  //     if (installReactRouter) {
  //       await downloadPackage('react-router-dom')
  //     }

  //     // Uncomment below when testing
  //     // process.exit()
  //   }

  //   // Call function that defines the prompts generation
  //   await promptRouteGeneration()
  // } else {
  //   logger.error('Route generation cancelled.')
  //   process.exit()
  // }
  try {
    const { generateRoutes }: { generateRoutes: boolean } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'generateRoutes',
        message: 'Want to generate routes?',
        default: false
      }
    ])

    if (!generateRoutes) {
      logger.error('Route generation cancelled.')
      process.exit()
    }

    const packageJson: PackageJson | null = parsePackageJson()
    logger.info('🚀 ~ promptIntroduction ~ packageJson:', packageJson)

    if (packageJson === null) {
      logger.error('No package.json found. Ensure you are in the root directory of your React project.')
      process.exit(1)
    }

    const hasReactRouter = 'react-router-dom' in (packageJson.dependencies ?? {}) || 'react-router-dom' in (packageJson.devDependencies ?? {})

    if (!hasReactRouter) {
      logger.error('React Router is not installed.')
      const { installReactRouter } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'installReactRouter',
          message: 'Do you want to install react-router-dom?',
          default: true
        }
      ])

      if (installReactRouter === true) {
        await downloadPackage('react-router-dom')
      } else {
        logger.error('Cannot proceed without React Router. Exiting...')
        // uncomment when testing prod
        // process.exit(1)
      }
    }

    await promptRouteGeneration()
  } catch (error) {
    logger.error('An unexpected error occurred:', error)
    process.exit(1)
  }
}

/**
 * Main function to prompt the user for the route generation and handle logical flow
 */
const promptRouteGeneration = async (): Promise<void> => {
  const answers = await inquirer.prompt([
    {
      // check for page/route folder in src or app
      type: 'confirm',
      name: 'hasPagesFolder',
      message: 'Do you have a pages/routes folder?',
      default: false
    }
  ])

  logger.info(answers)

  // check answers here
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { hasPagesFolder, serviceName, apiPath } = answers

  if (hasPagesFolder === false) {
    logger.break()
    logger.info('Confirming no routes or pages folder.')

    const { generationType }: { generationType: 'routes' | 'pages' } = await inquirer.prompt([
      {
        type: 'list',
        name: 'generationType',
        message: 'Choose what to generate:',
        choices: ['routes', 'pages'],
        default: 'route'
      }
    ])
    // call function to create a folder based on the generationType
    await createFolder(generationType)
  }

  // pages/routes folder has been created. Now we need to create the service/page
}

/**
 * Creates a folder based on the generationType
 * @param generationType The type of folder to create
 * @example
 * createFolder('pages')
 */
const createFolder = async (generationType: 'routes' | 'pages'): Promise<void> => {
  // need to check my working directory correct? make sure I am not in the wrong folder
  const cwd = process.cwd()
  let targetDir: string = cwd

  // Check for the presence of 'src' or 'app' directory inside the working directory
  const detectedSrc = await detectSourceDirectory()
  targetDir = path.join(cwd, detectedSrc)
  // TODO: Abstract this loop away with the pwd declaration above to have a reusable sourceDirectory finder
  // const preferredDirs = ['src', 'app']
  // for (const dir of preferredDirs) {
  //   if (fs.existsSync(path.join(cwd, dir))) {
  //     break
  //   }
  // }

  // Create a subdirectory titled (generationType) within the found directory
  const generationPath = path.join(targetDir, generationType)
  fs.mkdirSync(generationPath, { recursive: true })
  logger.break()
  logger.success(`🚀 ~ ${generationType} folder created at: ${generationPath}`)
}

/**
 * Detects the package manager used in the current project
 * @returns {string} The package manager used in the current project
 */
const getPackageManager = async (): Promise<'npm' | 'pnpm' | 'yarn' | 'yarn@berry' | 'pnpm@6' | 'bun'> => {
  const cwd = process.cwd()
  // use antfu/ni detect method to get the package manager
  const packageManager = await detect({ programmatic: true, cwd })
  logger.info('🚀 ~ getPackageManager ~ packageManager:', packageManager)
  return packageManager ?? 'npm'
}

/**
 * Downloads a package using the specified package manager
 * @param packageName The name of the package to download
 * @param manager The package manager to use
 * @example
 * downloadPackage('react-router-dom', 'npm')
 */
const downloadPackage = async (packageName: string): Promise<void> => {
  const manager: string = await getPackageManager()
  const { stdout, stderr } = await execa(manager, manager === 'npm' ? ['install', packageName] : ['add', packageName])
  stderr !== '' ? logger.error(stderr) : logger.success(stdout)
}
