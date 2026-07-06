import React from 'react';
import SchoolNavbar from '../components/school/SchoolNavbar';
import SchoolHero from '../components/school/SchoolHero';
import SchoolPreview from '../components/school/SchoolPreview';
import SchoolFeatures from '../components/school/SchoolFeatures';
import SchoolExamBoards from '../components/school/SchoolExamBoards';
import SchoolPricing from '../components/school/SchoolPricing';
import SchoolTestimonials from '../components/school/SchoolTestimonials';
import SchoolPhilosophy from '../components/school/SchoolPhilosophy';
import SchoolStory from '../components/school/SchoolStory';
import SchoolTeachers from '../components/school/SchoolTeachers';
import SchoolPlans from '../components/school/SchoolPlans';
import SchoolFAQs from '../components/school/SchoolFAQs';
import SchoolUpdates from '../components/school/SchoolUpdates';
import SchoolFooter from '../components/school/SchoolFooter';
import SchoolStats from '../components/school/SchoolStats';
import BoostDivider from '../components/shared/BoostDivider';

export default function SchoolPage() {
    return (
        <div className="min-h-screen flex flex-col">
            <SchoolNavbar />
            <SchoolHero />
            <SchoolPreview />
            <BoostDivider />
            <SchoolFeatures />
            <SchoolStats />
            <SchoolExamBoards />
            <BoostDivider />
            <SchoolPricing />
            <BoostDivider />
            <SchoolTestimonials />
            <SchoolPhilosophy />
            <SchoolStory />
            <SchoolTeachers />
            <SchoolPlans />
            <SchoolFAQs />
            <SchoolUpdates />
            <BoostDivider />
            <SchoolFooter />
        </div>
    );
}
