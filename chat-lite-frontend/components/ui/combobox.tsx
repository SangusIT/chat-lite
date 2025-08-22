import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { CheckIcon, ChevronsUpDownIcon } from "lucide-react"
import { useState } from "react"
import React from 'react';

interface ComboBoxProps {
    items: string[];
    list_type: string;
    onValueChange: Function
}

const ComboBox: React.FC<ComboBoxProps> = ({ items, list_type, onValueChange }) => {
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState("")
  const handleChange = (value: string) => {
    onValueChange(value);
  };
 
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {value
            ? items.find((item) => item === value)
            : `Select ${list_type}...`}
          <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder={`Select ${list_type}...`} />
          <CommandList>
            <CommandEmpty>{`No ${list_type} found.`}</CommandEmpty>
            <CommandGroup>
              {items.map((item) => (
                <CommandItem
                  key={item}
                  value={item}
                  onSelect={(currentValue) => {
                    setValue(currentValue === value ? "" : currentValue)
                    setOpen(false)
                    handleChange(currentValue === value ? "" : currentValue)
                  }}
                >
                  <CheckIcon
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === item ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {item}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

export default ComboBox;