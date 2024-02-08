# Art Institute of Chicago Collection Application Proposal

## Goal of the Application

The primary goal is to develop an interactive application that allows users to:
- View artworks from the Art Institute of Chicago's collection.
- Favorite artworks they appreciate.
- Filter artwork to discover pieces that align with their interests.

This application serves as a digital platform to explore the AIC collection and learn more about diverse artworks remotely.

## Target Audience

The site is envisioned as an educational tool and a supplemental resource for:
- Art enthusiasts.
- Educational institutions.
- Students and teachers.
- Museum visitors looking to extend their experience digitally.

## Data Usage

Data will be utilized from The Art Institute of Chicago’s API, with a focus on the following endpoints:
- Artwork
- Agents
- Category terms
- Artwork types


## Security Measures

- **User Passwords:** To ensure the confidentiality of user account information, passwords will be securely hashed before being stored in the database. This approach safeguards user passwords against unauthorized access and compromises.

## App Functionality

- **Artwork Filtering:** Users will be able to filter artworks based on their preferences, making the discovery of art pieces more personalized and engaging.
- **Favorites:** The application will allow users to save their favorite images, curating their own collection of liked artworks for easy access and review.

## User Flow

1. **Account Creation:** Users will start by creating an account through the Login/Signup Page.
2. **Artwork Discovery:** Upon logging in, the user's homepage will feature a randomly selected artwork, filtered based on the user's previous interactions and preferences.
3. **Favorites Collection:** Users will have the option to add artworks to their favorites collection, allowing them to keep track of the pieces they find most appealing.
4. **Surprise Feature:** A 'Surprise Me' feature will present artworks to the user that are outside of their favorites list, encouraging exploration and discovery of new pieces.



## Database Schema
The application will utilize a relational database with the following structure:  
- **Users**: Store user profiles and credentials.  
- **Artists**: Information about artists whose works are in the collection.  
- **Artworks**: Details of individual artworks.  
- **Favorites**: A junction table to connect users with their favorite artists and artworks.  


## API Challenges
- Image access: Image URLs will be built using metadata from the `image_id` field based on IIIF Image API conventions.
- Data consistency: Regular updates to ensure that the application’s database stays in sync with the AIC's API.


## Conclusion

The Interactive Artwork Discovery Platform will serve as a dynamic, educational tool for art enthusiasts and visitors of The Art Institute of Chicago. By leveraging the rich collection of the AIC and providing user-centric features, the application will promote engagement and appreciation of the arts in an accessible digital format.

For more information about the API and its documentation, please visit [The Art Institute of Chicago API Documentation](https://api.artic.edu/docs/).

---
