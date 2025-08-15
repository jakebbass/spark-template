'use client'

import { useState } from 'react'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/20/solid'

export default function DraftPage() {
  const [selectedTab, setSelectedTab] = useState('available')

  const tabs = [
    { id: 'available', name: 'Available' },
    { id: 'taken', name: 'Taken' }, 
    { id: 'queue', name: 'My Queue' },
    { id: 'advice', name: 'Advice' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Live Draft Board</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Round 1, Pick 1</span>
              <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                On the Clock
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* On the Clock Strip */}
        <div className="mb-6 rounded-lg bg-blue-50 p-4">
          <h2 className="text-lg font-medium text-blue-900 mb-3">Top Recommendations</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white rounded-lg p-4 shadow-sm border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Player {i}</p>
                    <p className="text-sm text-gray-500">RB • Team {i}</p>
                    <p className="text-sm text-blue-600">VORP: 25.{i}</p>
                  </div>
                  <button className="rounded bg-blue-600 px-3 py-1 text-xs text-white hover:bg-blue-700">
                    Draft
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Draft Board Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`${
                    selectedTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  } whitespace-nowrap border-b-2 py-4 px-6 text-sm font-medium`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {selectedTab === 'available' && <AvailablePlayersTab />}
            {selectedTab === 'taken' && <TakenPlayersTab />}
            {selectedTab === 'queue' && <QueueTab />}
            {selectedTab === 'advice' && <AdviceTab />}
          </div>
        </div>
      </main>
    </div>
  )
}

function AvailablePlayersTab() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium">Available Players</h3>
        <div className="flex items-center space-x-2">
          <select className="rounded border-gray-300 text-sm">
            <option>All Positions</option>
            <option>QB</option>
            <option>RB</option>
            <option>WR</option>
            <option>TE</option>
          </select>
        </div>
      </div>
      
      <div className="space-y-2">
        {Array.from({ length: 10 }, (_, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-500">#{i + 1}</span>
              <div>
                <p className="font-medium">Available Player {i + 1}</p>
                <p className="text-sm text-gray-500">RB • Team • VORP: {20 - i}.5</p>
              </div>
            </div>
            <button className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700">
              Add to Queue
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function TakenPlayersTab() {
  return (
    <div>
      <h3 className="text-lg font-medium mb-4">Drafted Players</h3>
      <div className="text-center text-gray-500 py-8">
        No players drafted yet
      </div>
    </div>
  )
}

function QueueTab() {
  return (
    <div>
      <h3 className="text-lg font-medium mb-4">My Draft Queue</h3>
      <div className="text-center text-gray-500 py-8">
        Add players to your queue to track your targets
      </div>
    </div>
  )
}

function AdviceTab() {
  return (
    <div>
      <h3 className="text-lg font-medium mb-4">AI Draft Advice</h3>
      <div className="bg-blue-50 rounded-lg p-4 mb-4">
        <h4 className="font-medium text-blue-900 mb-2">Recommendation</h4>
        <p className="text-blue-800">
          Focus on elite RB talent early. Consider Christian McCaffrey or Austin Ekeler 
          for their proven floor and upside potential in PPR scoring.
        </p>
      </div>
      
      <div className="space-y-3">
        <div className="border rounded-lg p-3">
          <h5 className="font-medium mb-1">Strategy: Zero RB</h5>
          <p className="text-sm text-gray-600">
            Wait on RBs and load up on elite WRs and QB early
          </p>
        </div>
        <div className="border rounded-lg p-3">
          <h5 className="font-medium mb-1">Strategy: Robust RB</h5>
          <p className="text-sm text-gray-600">
            Secure 2-3 solid RBs in the first 6 rounds
          </p>
        </div>
      </div>
    </div>
  )
}