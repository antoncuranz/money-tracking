'use client';

import React, { createContext, useContext } from 'react';
import {useMediaQuery} from "react-responsive";

type ResponsiveContextType = {
  isMobile: boolean;
};

const ResponsiveContextDefaultValues: ResponsiveContextType = {
  isMobile: false
};

const ResponsiveStateContext = createContext<ResponsiveContextType>(ResponsiveContextDefaultValues);

export const ResponsiveStateProvider = ({
  children
}: {
  children: React.ReactNode
}) => {
  const isMobile = useMediaQuery({ maxWidth: 750 }) // keep in sync with css media query

  return (
    <ResponsiveStateContext.Provider value={{ isMobile }}>
      {children}
    </ResponsiveStateContext.Provider>
  );
};

export const useResponsiveState = () => {
  return useContext(ResponsiveStateContext);
};