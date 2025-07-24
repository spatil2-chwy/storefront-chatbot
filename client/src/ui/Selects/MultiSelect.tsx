import * as React from "react"
import { X } from "lucide-react"
import { Badge } from "../Display/Badge"
import { Button } from "../Buttons/Button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "../ListItems/Command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../Overlay/Popover"
import { cn } from "../../lib/utils"

export interface MultiSelectOption {
  label: string
  value: string
}

interface MultiSelectProps {
  options: MultiSelectOption[]
  selectedValues: string[]
  onSelectionChange: (values: string[]) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyMessage?: string
  className?: string
  disabled?: boolean
}

export function MultiSelect({
  options,
  selectedValues,
  onSelectionChange,
  placeholder = "Select options...",
  searchPlaceholder = "Search options...",
  emptyMessage = "No options found.",
  className,
  disabled = false,
}: MultiSelectProps) {
  const [open, setOpen] = React.useState(false)

  const handleSelect = (value: string) => {
    if (selectedValues.includes(value)) {
      onSelectionChange(selectedValues.filter((v) => v !== value))
    } else {
      onSelectionChange([...selectedValues, value])
    }
  }

  const handleRemove = (value: string) => {
    onSelectionChange(selectedValues.filter((v) => v !== value))
  }

  const selectedOptions = options.filter((option) =>
    selectedValues.includes(option.value)
  )

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between border-gray-200 hover:border-gray-300 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 py-2 px-3 h-auto min-h-0 text-left",
            !selectedValues.length && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          {selectedValues.length === 0 ? (
            <span className="text-muted-foreground">{placeholder}</span>
          ) : (
            <div className="flex flex-wrap gap-1 w-full min-w-0">
              {selectedOptions.map((option) => (
                <Badge
                  key={option.value}
                  variant="secondary"
                  className="text-xs bg-purple-100 text-purple-800 border border-purple-200 flex-shrink-0 max-w-full truncate"
                >
                  {option.label}
                </Badge>
              ))}
            </div>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0 border border-gray-200 shadow-lg" align="start">
        <Command>
          <CommandInput placeholder={searchPlaceholder} className="border-0 focus:ring-0" />
          <CommandList className="max-h-[200px]">
            <CommandEmpty className="text-gray-500 py-2">{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option.value}
                  value={option.value}
                  onSelect={() => handleSelect(option.value)}
                  className="hover:bg-purple-50 focus:bg-purple-50"
                >
                  <div
                    className={cn(
                      "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-gray-300",
                      selectedValues.includes(option.value)
                        ? "bg-purple-500 border-purple-500 text-white"
                        : "opacity-50 [&_svg]:invisible"
                    )}
                  >
                    {selectedValues.includes(option.value) && (
                      <svg
                        className="h-3 w-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    )}
                  </div>
                  {option.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
} 