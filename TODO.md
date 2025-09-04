<!--
Copyright (C) 2025 Brighter Sight
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

For inquiries, contact: Info@BrighterSight.ca
-->

# Party Drink Tracker - TODO List

This file tracks planned improvements and future features for the Party Drink Tracker application.

## Future Improvements

### High Priority
- [ ] Add ability to create/add new users through the interface
- [ ] If connected to 'localhost' as a guest, show everybody's name.  If connected via a different I.P address, log the address and default to the same person. With the option of changing.
- [ ] Allow setting guest weights during initial setup
- [ ] Update remaining files to use constants
- [ ] Move project init/setup files to their own directory
- [ ] Get images from `https://github.com/bobbyc-brs/Test2-PartyApp/tree/main/drinks`


### Medium Priority
- [ ] Improve mobile responsiveness of both interfaces
- [ ] Add option to delete/undo drink entries in case of mistakes
- [ ] Implement user authentication for the host interface
- [ ] Add drink customization (custom ABV/volume)

### Low Priority
- [ ] Add dark mode toggle
- [ ] Create data export functionality (CSV/PDF)
- [ ] Implement drink suggestions based on current BAC
- [ ] Add internationalization support (i18n)

## Milestones
- [x] Initial version tagged as "v0.1.0-first-attempt"
- [x] Functional version tagged as "v0.3.0-working-with-bugs"

## Completed
- [x] Set up Python virtual environment and project structure
- [x] Create requirements.txt with necessary dependencies
- [x] Define data models for guests, drinks, and consumption tracking
- [x] Implement guest API (port 4000) for registering drinks
- [x] Implement host API (port 4001) for monitoring consumption
- [x] Create guest frontend with drink selection interface
- [x] Create host frontend with BAC visualization
- [x] Implement data source handling (guest-list, drink-list.csv, drink images)
- [x] Implement BAC calculation algorithm
- [x] Fix BAC calculation issues (metabolism over time, realistic starting values)
- [x] Create README with setup and usage instructions
- [x] Create utility scripts for setup, running, and cleanup
- [x] Implement placeholder image generation for drinks
- [x] Add root route redirects to fix 404 errors
- [x] Fix empty chart error in host dashboard
- [x] Fix chart display issues in host dashboard
- [x] Move the Status Pop-Ups for each drink to bottom of page
- [x] Fix time display: Convert UTC timestamps to local time for better user experience
- [x] Refactor magic numbers into constants (e.g., BAC calculation parameters, alcohol density)
  - [x] Created app/constants.py with documented constants
  - [x] Updated models.py to use constants
