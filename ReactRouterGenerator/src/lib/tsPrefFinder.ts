import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import { parsePackageJson } from './parsePkgJsn.ts'
import { logger } from './logger.ts'

/**
 * Attempts to detect TypeScript usage and preferences in the project.
 * @returns {Promise<{ usesTs: boolean, prefersTsx: boolean }>} TypeScript usage and TSX preference.
 */
export const detectTypeScriptPreferences = async (): Promise<{ usesTs: boolean, prefersTsx: boolean }> => {
  const tsConfigPath = path.join(process.cwd(), 'tsconfig.json')
  let usesTs = false
  let prefersTsx = false

  // Check for tsconfig.json to determine if it's a TypeScript project
  if (fs.existsSync(tsConfigPath)) {
    usesTs = true
    logger.info('TypeScript project detected.')

    // Parse tsconfig.json to check for TSX preference
    const tsConfig = fs.readJsonSync(tsConfigPath)
    prefersTsx = tsConfig.compilerOptions?.jsx !== undefined
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
