from django.core.management.base import BaseCommand
from main_app.models import Program


class Command(BaseCommand):
    help = 'Load initial government programs data'

    def handle(self, *args, **options):
        programs_data = [
            {
                'name': 'Enhanced Social Security Program',
                'description': 'Provides monthly financial support to the most needy families, integrated with charities to update beneficiary data and coordinate assistance.',
                'ministry_owner': 'Ministry of Human Resources and Social Development',
                'estimated_beneficiaries': 'More than 1.8 million families',
                'status': 'ACTIVE',
                'eligibility_criteria': 'Most needy families registered with charitable organizations',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',  # Money/Finance icon
            },
            {
                'name': 'Sakani Housing Program',
                'description': 'Provides housing solutions for families registered with charities and social security, including financing or free housing units.',
                'ministry_owner': 'Ministry of Municipal, Rural Affairs and Housing',
                'estimated_beneficiaries': 'More than 150,000 families annually',
                'status': 'ACTIVE',
                'eligibility_criteria': 'Families registered with charitable organizations and social security',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/3039/3039449.png',  # House/Home icon
            },
            {
                'name': 'Food Support Program (Food Support Card)',
                'description': 'Provides food cards or cash amounts to purchase food items for families registered with charitable organizations.',
                'ministry_owner': 'Ministry of Human Resources and Social Development in cooperation with charities',
                'estimated_beneficiaries': 'Approximately 1.2 million families',
                'status': 'ACTIVE',
                'eligibility_criteria': 'Families registered with charitable organizations',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/3081/3081559.png',  # Food/Grocery icon
            },
            {
                'name': 'Productive Families Financing Program',
                'description': 'Provides interest-free loans to poor families registered with charities to become productive and establish small businesses.',
                'ministry_owner': 'Social Development Bank (under the supervision of the Ministry of Human Resources and Social Development)',
                'estimated_beneficiaries': 'More than 17,000 families',
                'status': 'ACTIVE',
                'eligibility_criteria': 'Poor families registered with charitable organizations',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/3135/3135807.png',  # Business/Work icon
            },
            {
                'name': 'Home Renovation Program for Needy Families',
                'description': 'Funds maintenance and renovation of homes for needy families registered with charities, in coordination with developmental housing initiatives.',
                'ministry_owner': 'Ministry of Municipal Affairs and Housing in cooperation with local charitable organizations',
                'estimated_beneficiaries': 'Approximately 10,000 families annually',
                'status': 'ACTIVE',
                'eligibility_criteria': 'Needy families registered with charitable organizations',
                'icon_url': 'https://cdn-icons-png.flaticon.com/512/2942/2942935.png',  # Tools/Renovation icon
            },
        ]

        created_count = 0
        updated_count = 0

        for program_data in programs_data:
            program, created = Program.objects.update_or_create(
                name=program_data['name'],
                defaults={
                    'description': program_data['description'],
                    'ministry_owner': program_data['ministry_owner'],
                    'estimated_beneficiaries': program_data['estimated_beneficiaries'],
                    'status': program_data['status'],
                    'eligibility_criteria': program_data['eligibility_criteria'],
                    'icon_url': program_data.get('icon_url', ''),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {program.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {program.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully loaded {len(programs_data)} programs '
                f'({created_count} created, {updated_count} updated)'
            )
        )

