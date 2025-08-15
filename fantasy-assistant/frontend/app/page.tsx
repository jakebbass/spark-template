import Link from 'next/link'
import { ChartBarIcon, TrophyIcon, UserGroupIcon } from '@heroicons/react/24/outline'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Fantasy Draft Assistant
          </h1>
          <p className="mt-2 text-gray-600">
            AI-powered draft advice with advanced analytics
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {/* Rankings Card */}
          <div className="overflow-hidden rounded-lg bg-white shadow">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <ChartBarIcon className="h-8 w-8 text-blue-600" aria-hidden="true" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">Player Rankings</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    View ranked players with VORP, tiers, and projections
                  </p>
                </div>
              </div>
              <div className="mt-6">
                <Link
                  href="/rankings"
                  className="inline-flex items-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500"
                >
                  View Rankings
                </Link>
              </div>
            </div>
          </div>

          {/* Draft Card */}
          <div className="overflow-hidden rounded-lg bg-white shadow">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrophyIcon className="h-8 w-8 text-yellow-600" aria-hidden="true" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">Live Draft</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Real-time draft tracking with AI recommendations
                  </p>
                </div>
              </div>
              <div className="mt-6">
                <Link
                  href="/draft"
                  className="inline-flex items-center rounded-md bg-yellow-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-yellow-500"
                >
                  Start Draft
                </Link>
              </div>
            </div>
          </div>

          {/* League Sync Card */}
          <div className="overflow-hidden rounded-lg bg-white shadow">
            <div className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-8 w-8 text-green-600" aria-hidden="true" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-lg font-medium text-gray-900">League Sync</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Connect to Sleeper, ESPN, or Yahoo leagues
                  </p>
                </div>
              </div>
              <div className="mt-6">
                <button
                  disabled
                  className="inline-flex items-center rounded-md bg-gray-300 px-3 py-2 text-sm font-semibold text-gray-500"
                >
                  Coming Soon
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-gray-900">Features</h2>
          <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">VORP Analysis</h3>
              <p className="mt-2 text-sm text-gray-600">
                Value Over Replacement Player calculations with tier rankings
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Monte Carlo</h3>
              <p className="mt-2 text-sm text-gray-600">
                Season simulations for floor/ceiling analysis
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">Schedule Analysis</h3>
              <p className="mt-2 text-sm text-gray-600">
                Identify startable weeks and early-season value
              </p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900">AI Advice</h3>
              <p className="mt-2 text-sm text-gray-600">
                Real-time draft recommendations with explanations
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}