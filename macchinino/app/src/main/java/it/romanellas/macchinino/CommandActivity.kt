package it.romanellas.macchinino

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import java.io.IOException
import java.util.UUID
import kotlin.concurrent.thread

class CommandActivity : AppCompatActivity() {

    private lateinit var deviceName: String
    private lateinit var deviceAddress: String
    private var bluetoothSocket: BluetoothSocket? = null

    // You must use the same UUID as your server
    private val MY_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB") // SPP

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val tv = TextView(this)
        setContentView(tv)

        deviceName = intent.getStringExtra("device_name") ?: "Unknown"
        deviceAddress = intent.getStringExtra("device_address") ?: ""

        if (deviceAddress.isEmpty()) {
            Toast.makeText(this, "No device address provided", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        tv.text = "Connecting to $deviceName ($deviceAddress)..."

        thread {
            connectToDevice(tv)
        }
    }

    private fun connectToDevice(statusTextView: TextView) {
        val bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
        val device: BluetoothDevice = bluetoothAdapter.getRemoteDevice(deviceAddress)

        try {
            if (ActivityCompat.checkSelfPermission(
                    this,
                    Manifest.permission.BLUETOOTH_CONNECT
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                return
            }
            bluetoothSocket = device.createRfcommSocketToServiceRecord(MY_UUID)

            if (ActivityCompat.checkSelfPermission(
                    this,
                    Manifest.permission.BLUETOOTH_CONNECT
                ) != PackageManager.PERMISSION_GRANTED
            ) {
                return
            }
            bluetoothSocket?.connect()

            runOnUiThread {
                statusTextView.text = "Connected to $deviceName\nMAC: $deviceAddress"
                Toast.makeText(this, "Connected!", Toast.LENGTH_SHORT).show()
            }

            // You can now use bluetoothSocket!!.inputStream / outputStream

            sendString("")

        } catch (e: IOException) {
            e.printStackTrace()
            runOnUiThread {
                statusTextView.text = "Connection failed: ${e.message}"
                Toast.makeText(this, "Failed to connect", Toast.LENGTH_LONG).show()
            }

            try {
                bluetoothSocket?.close()
            } catch (closeEx: IOException) {
                closeEx.printStackTrace()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            bluetoothSocket?.close()
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    fun sendString(message: String) {
        try {
            bluetoothSocket?.outputStream?.write(message.toByteArray())
        } catch (e: IOException) {
            e.printStackTrace()
            Toast.makeText(this, "Failed to send: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }


}