import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import { parsePackageJson } from './parsePkgJsn.ts'
import { logger } from './logger.ts'
import stripJsonComments from 'strip-json-comments'

/**
 * Attempts to detect TypeScript usage and preferences in the project.
 * @returns {Promise<{ usesTs: boolean, prefersTsx: boolean }>} TypeScript usage and TSX preference.
 */
export const detectTypeScriptPreferences = async (): Promise<{ usesTs: boolean, prefersTsx: boolean }> => {
  const tsConfigPath = path.join(process.cwd(), 'tsconfig.json')
  logger.info('🚀 ~ detectTypeScriptPreferences ~ tsConfigPath:', tsConfigPath)
  let usesTs = false
  let prefersTsx = true

  // Check for tsconfig.json to determine if it's a TypeScript project
  if (fs.existsSync(tsConfigPath)) {
    usesTs = true
    logger.info('TypeScript project detected.')

    // Parse tsconfig.json to check for TSX preference
    // This errors because readJsonSync is reading a json file, but json files do not support comments, per se
    const tsConfig = fs.readFileSync(tsConfigPath, 'utf8')
    const tsConfigJson = JSON.parse(stripJsonComments(tsConfig))
    // logger.info('tsConfig', tsConfigJson)
    prefersTsx = tsConfigJson.compilerOptions?.jsx !== undefined
  } else {
    // Fallback or additional checks, e.g., parsing package.json or existing file extensions
    const packageJson = parsePackageJson()
    usesTs = packageJson?.devDependencies?.typescript !== undefined

    // This is a simplistic check;
    // TODO: Enhancing check by analyzing file extensions in the source directory
    if (usesTs) {
      logger.info('TypeScript dependency found in package.json.')
    }
  }

  // Ask the user if automatic detection is inconclusive or to confirm preferences
  if (usesTs) {
    const { extensionPreference } = await inquirer.prompt([
      {
        type: 'list',
        name: 'extensionPreference',
        message: 'Choose the preferred file extension for components:',
        choices: [{ name: 'TypeScript (TSX)', value: 'tsx' }, { name: 'JavaScript (JSX)', value: 'jsx' }],
        default: prefersTsx ? 'tsx' : 'jsx'
      }
    ])
    prefersTsx = extensionPreference === 'tsx'
  }

  return { usesTs, prefersTsx }
}
