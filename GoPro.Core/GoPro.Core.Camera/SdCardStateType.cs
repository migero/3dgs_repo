namespace GoPro.Core.Camera
{
	public enum SdCardStateType
	{
		NoWarning = 0,
		CardInserted = 1,
		CardEjected = 2,
		NoCard = 3,
		CardFull = 4,
		CardError = 5,
		MTPMode = 6,
		ShutDownState = 99
	}
}
