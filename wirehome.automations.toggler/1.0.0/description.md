# Summary
This automation toggles the power state of a component if a button was pressed.

# Configuration
* `buttons`: The list of buttons (component UIDs) which will trigger the toggle operation.
* `targets`: The list of target components (UIDs) which will receive the toggle command.

```
{
    "config": 
    {
        "buttons": [ "button1", "button2" ],
        "targets": [ "lamp1", "socket1" ]
    }
}
```