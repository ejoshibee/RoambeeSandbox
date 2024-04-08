import { type PackageJson } from 'type-fest'
// import { logger } from './logger.ts'
import fs from 'fs-extra'
import path from 'path'

/**
 * Parses the package.json file and returns the parsed json as a typed object.
 * @returns {PackageJson | null} The parsed json or null if the file is not found.
 */
export const parsePackageJson = (): PackageJson | null => {
  // use fs to read the package.json file
  const pkgJsn = fs.readJSONSync(path.join(process.cwd(), 'package.json'), 'utf8')

  // logger.info('🚀 ~ parsed json here', pkgJsn)

  // console.log('🚀 ~ parsePackageJson ~ pkgObj:', JSON.stringify(pkgObj, null, 2))
  return pkgJsn ?? null
}
