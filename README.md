# OverCRI
An EPITA bot to fetch users from their name.

![Banner of OverCRI](assets/overcri-logo.png)

## How to use:
### Groups
- `!!group <group-slug>`: Gets a random person from specified group
### People
- `!!login <login>`: Gets a person from exact login
- `!!random`: Gets a random person from all groups
- `!!firstname [lastname]`: Gets a person matching the best from both input, of course if you specify the lastname it has way better results
### Mappings
- `!!map <mapping-name>`: It maps the file sent to the mapping-name. ⚠️ This needs an attached file
- `!!define <mapping-name> any desc ...`: It adds a description to the said mapping
- `!!mappings`: Displays all mappings
- `!!<mapping-name>`: Sends back the file mapped
### Help
- `!!help`: Displays this message
