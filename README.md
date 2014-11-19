# Godef

This Sublime Text 3 [golang](golang.org) plugin adds a `godef` command which
uses [godef](http://godoc.org/code.google.com/p/rog-go/exp/cmd/godef) to find
the definition under the cursor.

#### Compatible with GoSublime

You can use this plugin working with [GoSublime](https://github.com/DisposaBoy/GoSublime) because GoSublime is not support `godef`.

## Installation

The plugin assumes `godef` is present at `$GOPATH/bin/godef`. You need install `godef` first:

    go get -v code.google.com/p/rog-go/exp/cmd/gode
    
#### Sublime Package Control

If you are using [Sublime Package Control](http://wbond.net/sublime_packages/package_control) you can simply install Sublime Reader by searching for `Godef` in the package listing.

#### Manual Install

Git clone this repository and place the entire `Godef` directory into your `Packages` directory.

OSX:

    # Install the plugin
    git clone git@github.com:buaazp/Godef.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Godef

Linux:

    # Install the plugin
    git clone git@github.com:buaazp/Godef.git ~/.config/sublime-text-3/Packages/Godef
    
Windows:


	Currently not supported.


## Settings

### Configuring `GOPATH`

Here's an example `Godef.sublime-settings`:

    {
        "gopath": "/Users/zippo/develop/GO"
    }

The plugin will determine `GOPATH` from either:

1. The `gopath` value from `Godef.sublime-settings`
2. The `GOPATH` environment variable


### Key Bindings

The default key of Godef is `super+d`. Here's an example key binding:

    { "keys": ["super+d"], "command": "godef" }

You can alse add these two key-binding to jump between the postions. Using j/k is because I use vim mode. Change them by yourself:

	{ "keys": ["super+j"], "command": "jump_forward"},
	{ "keys": ["super+k"], "command": "jump_back"},

Enjoy it!

## License

Godef is under BSD license which is in the license file.

This plugin is based on [GoTools](https://github.com/ironcladlou/GoTools) which is created by [Dan Mace](https://github.com/ironcladlou) and it's under MIT license:

```
The MIT License (MIT)

Copyright (c) 2014 Dan Mace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
