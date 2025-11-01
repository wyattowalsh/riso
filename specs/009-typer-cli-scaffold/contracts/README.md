# CLI Command Contracts

This directory contains interface contracts for the robust CLI scaffold. Since CLIs don't expose HTTP/GraphQL APIs, these contracts define the programmatic interfaces that commands, plugins, and framework components must implement.

## Contract Files

- [command-interface.py](./command-interface.py) - Base command interface that all commands must implement
- [plugin-interface.py](./plugin-interface.py) - Plugin registration interface
- [config-interface.py](./config-interface.py) - Configuration manager interface
- [formatter-interface.py](./formatter-interface.py) - Output formatter interface

## Contract Enforcement

These contracts are enforced through:

1. **Base classes** - Commands inherit from base command class
2. **Type hints** - MyPy validates adherence to protocols
3. **Runtime checks** - Plugin loader validates interface compliance
4. **Tests** - Contract tests verify implementations match interfaces

## Usage in Templates

Template files in `template/files/python/src/{{ package_name }}/cli/` implement these contracts to ensure consistency across generated CLI applications.
