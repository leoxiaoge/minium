# rcfile

> Loads library configuration in all possible ways

<!--@shields.flatSquare('npm', 'travis', 'coveralls')-->
[![npm version](https://img.shields.io/npm/v/rcfile.svg?style=flat-square)](https://www.npmjs.com/package/rcfile) [![Build Status](https://img.shields.io/travis/zkochan/rcfile/master.svg?style=flat-square)](https://travis-ci.org/zkochan/rcfile) [![Coverage Status](https://img.shields.io/coveralls/zkochan/rcfile/master.svg?style=flat-square)](https://coveralls.io/r/zkochan/rcfile?branch=master)
<!--/@-->

Read library configurations from `yaml`, `json`, `js` files or from sections in `package.json`.

## Installation

```sh
npm install --save rcfile
```

## Usage

```js
'use strict'
var rcfile = require('rcfile')

console.log(rcfile('eslint'))
//> { extends: 'standard',
//    rules:
//     { 'comma-dangle': [ 2, 'always-multiline' ],
//       'arrow-parens': [ 2, 'as-needed' ] } }

console.log(rcfile('travis', { configFileName: '.travis' }))
//> { language: 'node_js',
//    sudo: false,
//    node_js: [ 'v0.10', 'v4' ],
//    cache: { directories: [ 'node_modules' ] },
//    before_install: [ 'npm install -g npm@3' ],
//    install: [ 'npm install' ],
//    after_success:
//     [ 'if [[ $TRAVIS_NODE_VERSION == "v4" ]]; then npm run coveralls; fi;',
//       'if [[ $TRAVIS_NODE_VERSION == "v4" ]]; then npm run semantic-release; fi;' ] }
```

## License

[MIT](./LICENSE) © [Zoltan Kochan](http://kochan.io)

* * *

<!--@dependencies({ shield: 'flat-square' })-->
## <a name="dependencies">Dependencies</a> [![dependency status](https://img.shields.io/david/zkochan/rcfile/master.svg?style=flat-square)](https://david-dm.org/zkochan/rcfile/master)

- [debug](https://github.com/visionmedia/debug): small debugging utility
- [js-yaml](https://github.com/nodeca/js-yaml): YAML 1.2 parser and serializer
- [json5](https://github.com/aseemk/json5): JSON for the ES5 era.
- [object-assign](https://github.com/sindresorhus/object-assign): ES2015 Object.assign() ponyfill
- [object-keys](https://github.com/ljharb/object-keys): An Object.keys replacement, in case Object.keys is not available. From <https://github.com/es-shims/es5-shim>
- [path-exists](https://github.com/sindresorhus/path-exists): Check if a path exists
- [require-uncached](https://github.com/sindresorhus/require-uncached): Require a module bypassing the cache

<!--/@-->

<!--@devDependencies({ shield: 'flat-square' })-->
## <a name="dev-dependencies">Dev Dependencies</a> [![devDependency status](https://img.shields.io/david/dev/zkochan/rcfile/master.svg?style=flat-square)](https://david-dm.org/zkochan/rcfile/master#info=devDependencies)

- [chai](https://github.com/chaijs/chai): BDD/TDD assertion library for node.js and the browser. Test framework agnostic.
- [cz-conventional-changelog](https://github.com/commitizen/cz-conventional-changelog): Commitizen adapter following the conventional-changelog format.
- [eslint](https://github.com/eslint/eslint): An AST-based pattern checker for JavaScript.
- [eslint-config-standard](https://github.com/feross/eslint-config-standard): JavaScript Standard Style - ESLint Shareable Config
- [eslint-plugin-promise](https://github.com/xjamundx/eslint-plugin-promise): Enforce best practices for JavaScript promises
- [eslint-plugin-standard](https://github.com/xjamundx/eslint-plugin-standard): ESlint Plugin for the Standard Linter
- [ghooks](https://github.com/gtramontina/ghooks): Simple git hooks
- [istanbul](https://github.com/gotwarlost/istanbul): Yet another JS code coverage tool that computes statement, line, function and branch coverage with module loader hooks to transparently add coverage when running tests. Supports all JS coverage use cases including unit tests, server side functional tests
- [mocha](https://github.com/mochajs/mocha): simple, flexible, fun test framework
- [mos](https://github.com/mosjs/mos): A pluggable module that injects content into your markdown files via hidden JavaScript snippets
- [mos-plugin-readme](https://github.com/mosjs/mos-plugin-readme): A mos plugin for generating README
- [semantic-release](https://github.com/semantic-release/semantic-release): automated semver compliant package publishing
- [validate-commit-msg](https://github.com/kentcdodds/validate-commit-msg): Script to validate a commit message follows the conventional changelog standard

<!--/@-->
