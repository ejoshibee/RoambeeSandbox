#!/usr/bin/env node
import { init } from './commands/introduction.ts'
import { generate } from './commands/generate.ts'
import { Command } from 'commander'
import { parsePackageJson } from './lib/parsePkgJsn.ts'

process.on('SIGINT', () => process.exit(0))
process.on('SIGTERM', () => process.exit(0))

const main = async (): Promise<void> => {
  const packageInfo = parsePackageJson()

  const program = new Command()
    .name('route-generator')
    .description('A CLI tool to automate route and page generation for React projects.')
    .version(packageInfo?.version ?? '1.0.0',
      '-v, --version',
      'display the version number'
    )

  program.addCommand(generate).addCommand(init)

  program.parse()
}

await main()
