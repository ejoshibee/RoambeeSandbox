#!/usr/bin/env node

const { program } = require('commander');
const { generate } = require('../src/commands');

program
  .name("route-generator")
  .description("A CLI tool to automate route and page generation for React projects.")
  .version("1.0.0");

program
  .command('generate <name>')
  .description('Generate a new route and page')
  .action(generate);

program.parse(process.argv);
