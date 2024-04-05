/**
 * Module to parse package.json file and return an object with the parsed data.
 */

import { type PackageJson } from 'type-fest'
import { logger } from './logger.ts'

// const fs = require('fs-extra')
import fs from 'fs-extra'
// const path = require('path')
import path from 'path'

export const parsePackageJson = (): PackageJson => {
  // a function to parse package json for a specific package or packages
  // the function should take in a package name and return the parsed json
  // use fs to read the package.json file
  const pkgJsn = fs.readJSONSync(path.join(process.cwd(), 'package.json'), 'utf8') as PackageJson
  // parse the json

  logger.info('🚀 ~ parsed json here', pkgJsn)

  // console.log('🚀 ~ parsePackageJson ~ pkgObj:', JSON.stringify(pkgObj, null, 2))
  // return the parsed json
  return pkgJsn
}
