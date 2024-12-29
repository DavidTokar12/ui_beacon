# Welcome to UI Beacon

Bad practice:
```xml 
<Option value="Delete this message" action="Deletes this email" />
```

### Drop downs
```xml
<DropDown
    label=""  // One of label, description or icon is required. 
    description=""
    icon=""

    position= "" // Optional
>
    <Option
        value=""  // One of value or action is required
        action=""

        description=""  // Optional
        label="" // Optional
    />
</DropDown>
```

### Buttons