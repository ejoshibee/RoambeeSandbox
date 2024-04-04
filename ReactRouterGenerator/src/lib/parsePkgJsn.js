/**
 * Module to parse package.json file and return an object with the parsed data.
 * @module parsePackageJson
 */

// const fs = require('fs-extra')
import fs from 'fs-extra'
// const path = require('path')
import path from 'path'

export const parsePackageJson = () => {
    // a function to parse package json for a specific package or packages
    // the function should take in a package name and return the parsed json
    // use fs to read the package.json file
    const pkgJsn = fs.readJSONSync(path.join(process.cwd(), 'package.json'), 'utf8')
    // parse the json
    console.log('🚀 ~ parsePackageJson ~ pkgJsn:', pkgJsn)

    // console.log('🚀 ~ parsePackageJson ~ pkgObj:', JSON.stringify(pkgObj, null, 2))
    // return the parsed json
    // return pkgObj
}


