// const token = $('meta[name="csrf-token"]').attr('content');

// $('.fav-surprise').on('click', function(e) {
//     e.preventDefault();
//     const artworkId = $(this).data('artwork-id');
//     likeArtwork(artworkId, token);
// });



// Assuming the CSRF token is correctly set in a meta tag in your HTML head
const token = $('meta[name="csrf-token"]').attr('content');

$('.fav-surprise').on('click', function(e) {
    e.preventDefault();
    const artworkId = $(this).data('artwork-id');
    likeArtwork(artworkId, token);
});

async function likeArtwork(artworkId, csrfToken) {
    try {
        const response = await axios.post(`/users/favorites/${artworkId}`, {}, {
            headers: {
                'X-CSRFToken': csrfToken,
            }
        });
        if (response.data.success) {
            alert('Artwork liked!');
            // Optional: Update the UI to reflect the favorite status
        } else {
            alert(response.data.message);
        }
    } catch (error) {
        console.error('Error:', error.response.data);
        alert('An error occurred.');
    }
}
