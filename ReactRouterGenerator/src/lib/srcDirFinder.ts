import fs from 'fs-extra'
import path from 'path'
import inquirer from 'inquirer'
import chalk from 'chalk'
import { parsePackageJson } from './parsePkgJsn.ts'
// import ora from 'ora'
import { logger } from './logger.ts'

const commonSourceDirectories = ['src', 'app', 'lib', 'source']

/**
 * Attempts to auto-detect the source directory of the project.
*/
export const detectSourceDirectory = async (): Promise<string> => {
  // const spinner = ora(chalk.cyan('Detecting source directory...')).start()
  const cwd = process.cwd()
  const packageJson = parsePackageJson()
  const detectedDirectories = []
  // Check common directories and look for key files
  for (const dir of commonSourceDirectories) {
    const fullPath = path.join(cwd, dir)
    if (fs.existsSync(fullPath) && (fs.readdirSync(fullPath).find(file => /^(index|App)\.(js|jsx|ts|tsx)$/.test(file)) != null)) {
      logger.info(`Detected a potential source directory: ${dir}`)
      // spinner.text = chalk.cyan(`Detected a potential source directory: ${dir}`)
      logger.break()
      detectedDirectories.push(dir)
    }
  }

  // Analyze package.json scripts for hints
  if ((packageJson?.scripts) != null) {
    logger.info('Analyzing package.json scripts for additional clues...')
    // spinner.text = chalk.cyan('Analyzing package.json scripts for additional clues...')
    logger.break()
    const scriptValues = Object.values(packageJson.scripts)
    const scriptDirMatch = scriptValues.map(script => script?.match(/--out-dir\s+(\S+)/)).find(match => match)
    if ((scriptDirMatch?.[1]) != null) {
      // Add the directory from the script if it's not already included
      const scriptDir = scriptDirMatch[1].replace('./', '')
      if (!detectedDirectories.includes(scriptDir)) {
        detectedDirectories.push(scriptDir)
        logger.info(`Found additional source directory hint from package.json scripts: x${scriptDir}`)
        // spinner.text = chalk.cyan(`Found additional source directory hint from package.json scripts: ${scriptDir}`)
        logger.break()
      }
    }
  }

  // User confirmation or selection
  if (detectedDirectories.length === 1) {
    logger.info(`Auto-detected source directory: ${detectedDirectories[0]}`)
    // spinner.text = chalk.cyan(`Auto-detected source directory: ${detectedDirectories[0]}`)
    logger.break()

    const confirm = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'correct',
        message: `Detected source directory: ${chalk.green(detectedDirectories[0])}. Is this correct?`,
        default: true
      }
    ])
    if (confirm.correct === true) {
      // spinner.stop()
      return detectedDirectories[0]
    } else {
      logger.info('User indicated the detected directory is incorrect.')
      // spinner.text = chalk.cyan('User indicated the detected directory is incorrect.')
      logger.break()
    }
  } else if (detectedDirectories.length > 1) {
    logger.warn('Multiple potential source directories detected.')
    // spinner.text = chalk.yellow('Multiple potential source directories detected.')
    logger.break()
    const choice = await inquirer.prompt([
      {
        type: 'list',
        name: 'selectedDirectory',
        message: 'Select the correct source directory:',
        choices: detectedDirectories
      }
    ])
    // spinner.stop()
    return choice.selectedDirectory
  }

  // Fallback to manual input if unable to detect
  logger.warn('Unable to automatically detect the source directory. Please specify it manually.')
  // spinner.text = chalk.yellow('Unable to automatically detect the source directory. Please specify it manually.')
  logger.break()
  const manualInput = await inquirer.prompt([
    {
      type: 'input',
      name: 'directory',
      message: 'Enter your source directory:',
      default: 'src',
      validate: input => input !== '' || 'Please enter a directory name.'
    }
  ])
  // spinner.stop()
  return manualInput.directory
}
