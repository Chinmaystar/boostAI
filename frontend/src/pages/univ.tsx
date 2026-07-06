import React from 'react';
import UnivNavbar from '../components/univ/UnivNavbar';
import UnivHero from '../components/univ/UnivHero';
import UnivVideoPreview from '../components/univ/UnivVideoPreview';
import UnivTrust from '../components/univ/UnivTrust';
import SchoolPhilosophy from '../components/school/SchoolPhilosophy';
import UnivFeatures from '../components/univ/UnivFeatures';
import UnivPlans from '../components/univ/UnivPlans';
import UnivFAQs from '../components/univ/UnivFAQs';
import SchoolUpdates from '../components/school/SchoolUpdates';
import UnivFooter from '../components/univ/UnivFooter';
import BoostDivider from '../components/shared/BoostDivider';

export default function UnivPage() {
    return (
        <div className="min-h-screen flex flex-col">
            <UnivNavbar />
            <UnivHero />
            <UnivVideoPreview />
            <UnivTrust />
            <BoostDivider />
            <SchoolPhilosophy />
            <BoostDivider />
            <UnivFeatures />
            <BoostDivider />
            <UnivPlans />
            <UnivFAQs />
            <SchoolUpdates />
            <BoostDivider />
            <UnivFooter />
        </div>
    );
}
