import React, { useState } from 'react';
import { LifeStageDisplay } from './LifeStageDisplay';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Cards/Card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/Selects/Select';
import { Label } from '../ui/Input/Label';

export const LifeStageTest: React.FC = () => {
  const [selectedType, setSelectedType] = useState('DOG');
  const [selectedBirthday, setSelectedBirthday] = useState('');

  const petTypes = [
    { value: 'DOG', label: 'Dog' },
    { value: 'CAT', label: 'Cat' },
    { value: 'HORSE', label: 'Horse' },
    { value: 'BIRD', label: 'Bird' },
    { value: 'FISH', label: 'Fish' },
    { value: 'FARM_ANIMAL', label: 'Farm Animal' },
    { value: 'SMALL_PET', label: 'Small Pet' }
  ];

  // Sample birthdays for testing different life stages
  const sampleBirthdays = [
    { label: 'Newborn (1 day old)', value: new Date().toISOString().split('T')[0] },
    { label: '1 month old', value: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '6 months old', value: new Date(Date.now() - 6 * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '1 year old', value: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '2 years old', value: new Date(Date.now() - 2 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '5 years old', value: new Date(Date.now() - 5 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '10 years old', value: new Date(Date.now() - 10 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] },
    { label: '15 years old', value: new Date(Date.now() - 15 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] }
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Life Stage Calculator Test</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Test Life Stage Calculation</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-sm font-medium">Pet Type</Label>
            <Select
              value={selectedType}
              onValueChange={setSelectedType}
            >
              <SelectTrigger className="mt-1">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {petTypes.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label className="text-sm font-medium">Birthday</Label>
            <Select
              value={selectedBirthday}
              onValueChange={setSelectedBirthday}
            >
              <SelectTrigger className="mt-1">
                <SelectValue placeholder="Select a sample birthday" />
              </SelectTrigger>
              <SelectContent>
                {sampleBirthdays.map(birthday => (
                  <SelectItem key={birthday.value} value={birthday.value}>
                    {birthday.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="mt-6 p-4 bg-gray-100 rounded-md">
            <h3 className="font-semibold mb-2">Calculated Life Stage:</h3>
            <LifeStageDisplay
              petType={selectedType}
              birthday={selectedBirthday || null}
              showAge={true}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Life Stage Thresholds by Pet Type</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-semibold">Dogs:</h4>
              <p>• Puppy: 0-12 months</p>
              <p>• Adult: 1-7 years</p>
              <p>• Senior: 7+ years</p>
            </div>
            <div>
              <h4 className="font-semibold">Cats:</h4>
              <p>• Kitten: 0-12 months</p>
              <p>• Adult: 1-10 years</p>
              <p>• Senior: 10+ years</p>
            </div>
            <div>
              <h4 className="font-semibold">Horses:</h4>
              <p>• Foal: 0-3 years</p>
              <p>• Adult: 3-20 years</p>
              <p>• Senior: 20+ years</p>
            </div>
            <div>
              <h4 className="font-semibold">Fish:</h4>
              <p>• Juvenile: 0-6 months</p>
              <p>• Adult: 0.5-5 years</p>
              <p>• Senior: 5+ years</p>
            </div>
            <div>
              <h4 className="font-semibold">Hamsters:</h4>
              <p>• Baby: 0-2 months</p>
              <p>• Adult: 2-18 months</p>
              <p>• Senior: 18+ months</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}; 