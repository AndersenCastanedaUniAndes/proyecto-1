import React from 'react';

// Lightweight mocks for Popover to avoid complex DOM/querySelector usage in jsdom
export const Popover = ({ children }: React.PropsWithChildren) => <div>{children}</div>;
export const PopoverTrigger = ({ children }: React.PropsWithChildren) => <div data-slot="popover-trigger">{children}</div>;
export const PopoverContent = ({ children }: React.PropsWithChildren) => <div>{children}</div>;
