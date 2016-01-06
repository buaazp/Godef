# Godef

This Sublime Text 2/3 [golang](http://golang.org/) plugin adds a `godef` command which uses [godef](http://godoc.org/github.com/rogpeppe/godef) to find the definition under the cursor.

#### Compatible with GoSublime

You can use this plugin working with [GoSublime](https://github.com/DisposaBoy/GoSublime) because GoSublime is not support `godef`.

## Installation

The plugin assumes `godef` is present at `$GOPATH/bin/godef`. You need install `godef` first:

```
go get -v github.com/rogpeppe/godef
```

NOTE: If you upgrade you go runtime version, for example from 1.4.1 to 1.4.2, you need to rebuild the `godef` to find the correct postion of runtime src:

```
cd $GOPATH/src/github.com/rogpeppe/godef
go clean -r -i
go install -v
```

#### Sublime Package Control

If you are using [Sublime Package Control](http://wbond.net/sublime_packages/package_control) you can simply install Sublime Godef by searching for `Godef` in the package listing.

#### Manual Install

Git clone this repository and place the entire `Godef` directory into your `Packages` directory.

OSX:

```
# Install the plugin
git clone git@github.com:buaazp/Godef.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Godef
```

Linux:

```
# Install the plugin
git clone git@github.com:buaazp/Godef.git ~/.config/sublime-text-3/Packages/Godef
```

Windows:

Now windows is been supported. Thanks for [@decker502](https://github.com/decker502) and [@mattn](https://github.com/mattn)'s work.  Please use the Sublime Package Control to install this plugin.

## Settings

### Configuring `GOPATH` and `GOROOT`

In most cases, you needn't set anything after installing. But if your `Godef` don't work you need to add gopath and goroot into the setting file before using this plugin. Here's an example `Godef.sublime-settings`:

```
{
	"goroot": "/Users/zippo/Go",
	"gopath": "/Users/zippo/gopath"
}

// or if you use windows
{
	"goroot": "C:\\Go",
	"gopath": "C:\\gopath"
}
```

NOTE: The value of `gopath/goroot` should be absolute path. Multiple path like env `GOPATH` are supported but relative path are not:

```
GOOD:
"gopath": "/opt/golang:/Users/zippo/develop/GO"

BAD:
"gopath": "~/develop/GO"
"gopath": "$HOME/develop/GO"
```

 This plugin will determine `GOPATH/GOROOT` from either:

1. The `gopath/goroot` value from `Godef.sublime-settings`
2. The `GOPATH/GOROOT` environment variable

NOTE 2: In case your plugin can't resolve internals, add the installed library path to your gopath (notice the last part):

```
"gopath": "/opt/golang:/Users/zippo/develop/GO:/usr/lib/go"
```

#### Vendor Experiment

Add this to your configurations:
```
"GO15VENDOREXPERIMENT": "1",
```



### Key Bindings

The default key of Godef is `gd`, which is also the default key of godef plugin for vim. Don't be afraid. This key binding will NOT modify your codes. Just press it.

Or you can click left button while pressing `super/ctrl+alt`. You CAN of course change it by yourself. Here's an example key binding:

```
{ "keys": ["super+h"], "command": "godef" }
```

You can also add these two key-binding into your keymap file to jump between the postions. Using j/k is because I use vim mode. Change them by yourself:

```
{ "keys": ["super+j"], "command": "jump_forward"},
{ "keys": ["super+k"], "command": "jump_back"},
```

Enjoy it!

## License

Godef is under BSD license which is in the license file.


