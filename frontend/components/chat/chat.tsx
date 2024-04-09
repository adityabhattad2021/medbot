import React from 'react'
import ChatTopbar from './chat-topbar'
import ChatList from './chat-list'
import ChatBottombar from './chat-bottombar'
import { type Message } from 'ai/react';
import { ChatRequestOptions } from 'ai';
import { UserType } from '@/lib/user-type';

export interface ChatProps {
  chatId?: string,
  setSelectedModel?: React.Dispatch<React.SetStateAction<string>>;
  messages: Message[];
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>, chatRequestOptions?: ChatRequestOptions) => void;
  isLoading: boolean;
  loadingSubmit?: boolean;
  error?: undefined | Error;
  completion:string;
  stop: () => void;
  user:UserType
  }

export default function Chat ({ messages, input, handleInputChange, handleSubmit, isLoading, error, stop, setSelectedModel, chatId, loadingSubmit,completion,user }: ChatProps) {

  return (
    <div className="flex flex-col justify-between w-full h-full  ">
        <ChatTopbar
          user={user}  
          isLoading={isLoading}
          chatId={chatId} 
          messages={messages} 
        />
        <ChatList  
          completion={completion}
          messages={messages}
          isLoading={isLoading}
          loadingSubmit={loadingSubmit}
        />
        <ChatBottombar 
          input={input}
          handleInputChange={handleInputChange}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          stop={stop}
        />
    </div>
  )
}
