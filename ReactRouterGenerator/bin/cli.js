#!/usr/bin/env node
import { init } from '../src/commands/introduction.js'

import { program } from 'commander';

program
  .name("route-generator")
  .description("A CLI tool to automate route and page generation for React projects.")
  .version("1.0.0");

program
  .command('init')
  .description('Generate a new route and page')
  .action(init);

program.parse(process.argv);
