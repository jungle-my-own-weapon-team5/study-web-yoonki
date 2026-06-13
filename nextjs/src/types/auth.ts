export type CurrentUser = {
  id: number;
  email: string;
  nickname: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  nickname: string;
  password: string;
};
