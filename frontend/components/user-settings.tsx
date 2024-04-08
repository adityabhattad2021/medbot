'use client'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { GearIcon } from '@radix-ui/react-icons'
import { useEffect, useState } from 'react'
import { SettingsModal } from './settings-modal'
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar'
import { Button } from './ui/button'
import { Skeleton } from './ui/skeleton'
import { UserType } from '@/lib/user-type'

interface UserSettingsProps {
  user:UserType
}

export default function UserSettings(
  { user }: UserSettingsProps
) {
  const [name, setName] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [open, setOpen] = useState(false)

  useEffect(()=>{
    if(user?.user_name){
      setIsLoading(false)
    }
  },[user?.user_name])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex justify-start gap-3 w-full h-14 text-base font-normal items-center "
        >
          <Avatar className="flex justify-start items-center overflow-hidden">
            <AvatarImage
              src=""
              alt="AI"
              width={4}
              height={4}
              className="object-contain"
            />
            <AvatarFallback>
              {user?.user_name && user.user_name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="text-xs truncate">
            {isLoading ? (
              <Skeleton className="w-20 h-4" />
            ) : (
              user?.user_name || "Why?"
            )}
          </div>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-48 p-2">
        <Dialog>
          <DialogTrigger className="w-full">
            <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
              <div className="flex w-full gap-2 p-1 items-center cursor-pointer">
                <GearIcon className="w-4 h-4" />
                Settings
              </div>
            </DropdownMenuItem>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader className="space-y-4">
              <DialogTitle>Settings</DialogTitle>
              <SettingsModal setOpen={setOpen} />
            </DialogHeader>
          </DialogContent>
        </Dialog>
        <Dialog></Dialog>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
