export type CharacterStyle = 'modern' | 'fantasy' | 'sci-fi' | 'historical';

export type BodyType = 'athletic' | 'slim' | 'muscular' | 'heavy';
export type AgeRange = 'child' | 'teen' | 'adult' | 'elderly';

export interface CharacterAttributes {
    bodyType?: BodyType;
    ageRange?: AgeRange;
    [key: string]: any;
}

export interface GenerateCharacterResponse {
    id: string;
    modelData: any;
    traits: Record<string, number>;
    style: CharacterStyle;
    attributes: CharacterAttributes;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    progress: number;
    error?: string;
}

export interface APIError {
    error: string;
    message?: string;
    details?: any;
}

export interface SnackbarState {
    open: boolean;
    message: string;
    severity?: 'success' | 'error' | 'info' | 'warning';
}
