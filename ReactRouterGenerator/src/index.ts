#!/usr/bin/env node
import { init } from './commands/introduction.ts'
import { generate } from './commands/generate.ts'

import { program } from 'commander'

process.on('SIGINT', () => process.exit(0))
process.on('SIGTERM', () => process.exit(0))

program
  .name('route-generator')
  .description('A CLI tool to automate route and page generation for React projects.')
  .version('1.0.0')

program
  .command('init')
  .description('Generate a new route and page')
  .action(init)

program.command('generate').description('Generate a new route and page').action(generate)

program.parse(process.argv)
