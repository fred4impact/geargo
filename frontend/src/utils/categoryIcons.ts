/**
 * Maps category names to beautiful emoji icons
 */
export const getCategoryIcon = (categoryName: string, icon?: string): string => {
  // If icon is provided and it's not a Font Awesome class, use it
  if (icon && !icon.startsWith('fas fa-') && !icon.startsWith('fa-')) {
    return icon;
  }

  // Map category names to appropriate emoji icons
  const categoryNameLower = categoryName.toLowerCase();
  
  if (categoryNameLower.includes('bike') || categoryNameLower.includes('bicycle') || categoryNameLower.includes('cycle')) {
    return '🚴';
  }
  
  if (categoryNameLower.includes('instrument') || categoryNameLower.includes('music') || categoryNameLower.includes('guitar') || categoryNameLower.includes('piano') || categoryNameLower.includes('drum')) {
    return '🎸';
  }
  
  if (categoryNameLower.includes('sound') || categoryNameLower.includes('audio') || categoryNameLower.includes('speaker') || categoryNameLower.includes('microphone') || categoryNameLower.includes('mixer')) {
    return '🔊';
  }
  
  if (categoryNameLower.includes('gear') || categoryNameLower.includes('equipment')) {
    return '⚙️';
  }
  
  if (categoryNameLower.includes('media') || categoryNameLower.includes('camera') || categoryNameLower.includes('video') || categoryNameLower.includes('photo')) {
    return '📷';
  }
  
  if (categoryNameLower.includes('sport') || categoryNameLower.includes('fitness') || categoryNameLower.includes('gym')) {
    return '🏋️';
  }
  
  if (categoryNameLower.includes('electronic') || categoryNameLower.includes('tech') || categoryNameLower.includes('computer') || categoryNameLower.includes('laptop')) {
    return '💻';
  }
  
  if (categoryNameLower.includes('tool') || categoryNameLower.includes('hardware')) {
    return '🔧';
  }
  
  if (categoryNameLower.includes('vehicle') || categoryNameLower.includes('car') || categoryNameLower.includes('auto')) {
    return '🚗';
  }
  
  if (categoryNameLower.includes('outdoor') || categoryNameLower.includes('camping') || categoryNameLower.includes('hiking')) {
    return '⛺';
  }
  
  if (categoryNameLower.includes('party') || categoryNameLower.includes('event') || categoryNameLower.includes('celebration')) {
    return '🎉';
  }
  
  if (categoryNameLower.includes('furniture') || categoryNameLower.includes('chair') || categoryNameLower.includes('table') || categoryNameLower.includes('sofa')) {
    return '🪑';
  }
  
  if (categoryNameLower.includes('kitchen') || categoryNameLower.includes('cooking') || categoryNameLower.includes('appliance')) {
    return '🍳';
  }
  
  if (categoryNameLower.includes('book') || categoryNameLower.includes('reading') || categoryNameLower.includes('library')) {
    return '📚';
  }
  
  if (categoryNameLower.includes('game') || categoryNameLower.includes('gaming') || categoryNameLower.includes('console')) {
    return '🎮';
  }
  
  if (categoryNameLower.includes('other') || categoryNameLower.includes('misc')) {
    return '📦';
  }
  
  // Default icon
  return '📦';
};
