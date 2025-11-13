import * as React from "react"

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  checked: boolean
  onCheckedChange: () => void
}

export const Checkbox: React.FC<CheckboxProps> = ({ checked, onCheckedChange, ...props }) => {
  return (
    <input
      type="checkbox"
      checked={checked}
      onChange={onCheckedChange}
      {...props}
      className="w-4 h-4 accent-indigo-600 rounded border-gray-300 focus:ring-indigo-500"
    />
  )
}
