"use client"

import {Calendar} from "@/components/ui/calendar.tsx";
import {DayModifiers, ModifiersStyles} from "react-day-picker";
import {CSSProperties, useEffect, useState} from "react";
import {AccountDates} from "@/types.ts";

const DueDateCalendar = () => {
  
  const [dueDates, setDueDates] = useState<{ [id: string] : AccountDates; }>({});
  const [month, setMonth] = useState<Date>(new Date());
  
  useEffect(() => {
    updateDates()
  }, []);
  async function updateDates() {
    await onCalendarMonthChange(new Date())
  }
  
  function getModifiers(): DayModifiers {
    const modifiers: { [cls: string]: Date[] } = {
      dueDates: Object.values(dueDates).map(x => new Date(x.due)),
      statementDates: Object.values(dueDates).map(x => new Date(x.statement))
    }

    for (const accountDates of Object.values(dueDates)) {
      modifiers["due-" + accountDates.due] = [new Date(accountDates.due)]
      modifiers["statement-" + accountDates.statement] = [new Date(accountDates.statement)]
    }

    return modifiers
  }

  function getModifiersStyles(): ModifiersStyles {
    const modifiers: { [cls: string]: CSSProperties } = {}
    
    const accountDates = Object.values(dueDates)
    const dues = groupByDate(accountDates, "due")
    const statements = groupByDate(accountDates, "statement")
    
    // Assumption: There are no dates, at which dues and statements overlap
    
    for (const [dueDate, colors] of Object.entries(dues)) {
      const background = colors.length == 1 ? colors[0] : "linear-gradient(" + colors.join(", ") + ")"
      modifiers["due-" + dueDate] = {
        background: background
      }
    }

    for (const [statementDate, colors] of Object.entries(statements)) {
      const newColors = colors.length == 1 ? [colors[0], colors[0]] : colors
      const background = "linear-gradient(white 0 0) padding-box, linear-gradient(" + newColors.join(", ") + ") border-box"
      
      modifiers["statement-" + statementDate] = {
        background: background
      }
    }

    return modifiers
  }
  
  function groupByDate(data: AccountDates[], key: 'statement' | 'due'): {[date: string]: string[]} {
    return data.reduce((acc, { color, [key]: date }) => {
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(color);
      return acc;
    }, {} as { [date: string]: string[] });
  }
  
  async function onCalendarMonthChange(month: Date) {
    const response = await fetch("/api/dates/" + month.getFullYear() + "/" + (month.getMonth()+1))
    const dueDates = await response.json() as { [id: string] : AccountDates; }
    setDueDates(dueDates)
    setMonth(month)
  }

  return (
    <Calendar
        month={month}
        onMonthChange={onCalendarMonthChange}
        modifiers={getModifiers()}
        modifiersStyles={getModifiersStyles()}
        modifiersClassNames={{
          dueDates: "cal-due",
          statementDates: "cal-statement"
        }}
    />
  )
}

export default DueDateCalendar