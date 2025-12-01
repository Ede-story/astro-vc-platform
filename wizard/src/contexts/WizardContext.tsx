'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { DigitalTwin } from '@/types/astro';

// Birth data from step 1
export interface BirthData {
  date: string;
  time: string;
  city: string;
  lat: number;
  lon: number;
  timezone: number;
  ayanamsa: string;
  timeAccuracy: 'exact' | 'approximate' | 'unknown';
}

// Profile data from step 2
export interface ProfileData {
  username: string;
  fullName: string;
  bio: string;
  career: string;
  avatarUrl: string | null;
}

// Psych scores from calibration step
export interface PsychScores {
  energy: number;
  focus: number;
  decisions: number;
  structure: number;
  conflict: number;
  drive: number;
  novelty: number;
  interest_sphere: number;
  role: number;
  communication: number;
}

// Interests from step 3
export interface InterestsData {
  seeking: string[];
  offerings: string[];
}

// Complete wizard state
export interface WizardState {
  birthData: BirthData;
  profileData: ProfileData;
  interestsData: InterestsData;
  digitalTwin: DigitalTwin | null;
  currentStep: number;
}

const defaultBirthData: BirthData = {
  date: '',
  time: '',
  city: '',
  lat: 0,
  lon: 0,
  timezone: 0,
  ayanamsa: 'raman',
  timeAccuracy: 'exact',
};

const defaultProfileData: ProfileData = {
  username: '',
  fullName: '',
  bio: '',
  career: '',
  avatarUrl: null,
};

const defaultInterestsData: InterestsData = {
  seeking: [],
  offerings: [],
};

interface WizardContextType {
  state: WizardState;
  setBirthData: (data: Partial<BirthData>) => void;
  setProfileData: (data: Partial<ProfileData>) => void;
  setInterestsData: (data: Partial<InterestsData>) => void;
  setDigitalTwin: (twin: DigitalTwin | null) => void;
  setCurrentStep: (step: number) => void;
  resetWizard: () => void;
}

const WizardContext = createContext<WizardContextType | null>(null);

export function WizardProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WizardState>({
    birthData: defaultBirthData,
    profileData: defaultProfileData,
    interestsData: defaultInterestsData,
    digitalTwin: null,
    currentStep: 1,
  });

  const setBirthData = (data: Partial<BirthData>) => {
    setState(prev => ({
      ...prev,
      birthData: { ...prev.birthData, ...data },
    }));
  };

  const setProfileData = (data: Partial<ProfileData>) => {
    setState(prev => ({
      ...prev,
      profileData: { ...prev.profileData, ...data },
    }));
  };

  const setInterestsData = (data: Partial<InterestsData>) => {
    setState(prev => ({
      ...prev,
      interestsData: { ...prev.interestsData, ...data },
    }));
  };

  const setDigitalTwin = (twin: DigitalTwin | null) => {
    setState(prev => ({ ...prev, digitalTwin: twin }));
  };

  const setCurrentStep = (step: number) => {
    setState(prev => ({ ...prev, currentStep: step }));
  };

  const resetWizard = () => {
    setState({
      birthData: defaultBirthData,
      profileData: defaultProfileData,
      interestsData: defaultInterestsData,
      digitalTwin: null,
      currentStep: 1,
    });
  };

  return (
    <WizardContext.Provider
      value={{
        state,
        setBirthData,
        setProfileData,
        setInterestsData,
        setDigitalTwin,
        setCurrentStep,
        resetWizard,
      }}
    >
      {children}
    </WizardContext.Provider>
  );
}

export function useWizard() {
  const context = useContext(WizardContext);
  if (!context) {
    throw new Error('useWizard must be used within WizardProvider');
  }
  return context;
}
