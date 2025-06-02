from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: str | None = None
    city: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str


class UserSignupRequest(BaseModel):
    email: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    city: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserOutToken(BaseModel):
    id: int
    name: str
    email: str
    city: str | None
    is_active: bool
    access_token : str
    refresh_token : str

    model_config = ConfigDict(from_attributes=True)


class OTPVerify(BaseModel):
    email: str
    otp: str

class otpStatus(BaseModel):
    status: str

class SignupVerifiedOtp(BaseModel):
    email: str
    name: str
    password: str
    status: str
    phone_number: str | None = None
    city: str | None = None