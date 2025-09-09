<template>
  <div 
    :class="avatarClasses"
    :title="user.full_name || user.username || user.name"
    @click="handleClick"
  >
    <!-- Show thumbnail if available -->
    <img 
      v-if="thumbnailUrl && !imageError"
      :src="thumbnailUrl"
      :alt="user.full_name || user.username || user.name"
      class="w-full h-full object-cover"
      @load="onImageLoad"
      @error="onImageError"
    />
    
    <!-- Fallback to initials if no thumbnail or loading failed -->
    <span 
      v-if="!thumbnailUrl || imageError"
      :class="textClasses"
    >
      {{ getInitials(user) }}
    </span>
  </div>
</template>

<script>
export default {
  name: 'UserAvatar',
  emits: ['click'],
  props: {
    user: {
      type: Object,
      required: true
    },
    size: {
      type: String,
      default: 'md', // xs, sm, md, lg, xl
      validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
    },
    clickable: {
      type: Boolean,
      default: true
    },
    gradient: {
      type: String,
      default: 'blue-purple' // blue-purple, indigo, red, gray
    }
  },
  data() {
    return {
      imageLoaded: true,  // Start with true to show image immediately
      imageError: false
    }
  },
  computed: {
    thumbnailUrl() {
      // Get thumbnail URL from user profile
      if (this.user.profile?.avatar_thumbnail_url) {
        const url = this.user.profile.avatar_thumbnail_url
        // Add base URL if it's a relative path
        return url.startsWith('http') ? url : `http://localhost:8000${url}`
      }
      
      // If we have avatar URL, construct thumbnail URL
      if (this.user.profile?.avatar) {
        const avatarUrl = this.user.profile.avatar
        // Handle both full URLs and relative paths
        const baseUrl = avatarUrl.startsWith('http') ? '' : 'http://localhost:8000'
        
        const parts = avatarUrl.split('.')
        if (parts.length > 1) {
          const ext = parts.pop()
          const name = parts.join('.')
          return `${baseUrl}${name}_thumbnail.${ext}`
        }
      }
      
      return null
    },
    
    sizeClasses() {
      const sizes = {
        xs: 'w-6 h-6',
        sm: 'w-8 h-8',
        md: 'w-10 h-10 sm:w-12 sm:h-12',
        lg: 'w-12 h-12 sm:w-16 sm:h-16',
        xl: 'w-16 h-16 sm:w-20 sm:h-20'
      }
      return sizes[this.size] || sizes.md
    },
    
    textSizes() {
      const sizes = {
        xs: 'text-[10px]',
        sm: 'text-xs',
        md: 'text-sm sm:text-lg',
        lg: 'text-lg sm:text-xl',
        xl: 'text-xl sm:text-2xl'
      }
      return sizes[this.size] || sizes.md
    },
    
    gradientClasses() {
      const gradients = {
        'blue-purple': 'bg-gradient-to-br from-blue-500 to-purple-600',
        'indigo': 'bg-indigo-600',
        'red': 'bg-red-600',
        'gray': 'bg-gray-400'
      }
      return gradients[this.gradient] || gradients['blue-purple']
    },
    
    avatarClasses() {
      return [
        this.sizeClasses,
        'rounded-full flex items-center justify-center text-white font-semibold overflow-hidden',
        this.clickable ? 'cursor-pointer hover:scale-110 transition-transform duration-200' : '',
        !this.thumbnailUrl || this.imageError ? this.gradientClasses : '',
        'border-2 border-white shadow-sm flex-shrink-0'
      ].filter(Boolean).join(' ')
    },
    
    textClasses() {
      return [
        this.textSizes,
        'font-semibold'
      ].join(' ')
    }
  },
  
  methods: {
    getInitials(user) {
      const name = user.full_name || user.username || user.name || 'User'
      return name.charAt(0).toUpperCase()
    },
    
    onImageLoad() {
      console.log('UserAvatar - Image loaded successfully:', this.thumbnailUrl)
      this.imageLoaded = true
      this.imageError = false
    },
    
    onImageError(event) {
      console.log('UserAvatar - Image load error:', this.thumbnailUrl, event)
      this.imageError = true
      this.imageLoaded = false
    },
    
    handleClick(event) {
      event.stopPropagation()
      this.$emit('click', this.user)
    }
  },
  
  watch: {
    thumbnailUrl() {
      // Reset image state when URL changes
      this.imageLoaded = false
      this.imageError = false
    }
  },
  
  mounted() {
    // Force image loading if thumbnailUrl exists
    if (this.thumbnailUrl) {
      const testImg = new Image()
      testImg.onload = () => {
        this.imageLoaded = true
        this.imageError = false
      }
      testImg.onerror = (e) => {
        this.imageError = true
        this.imageLoaded = false
      }
      testImg.src = this.thumbnailUrl
    }
  }
}
</script>
