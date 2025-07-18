package it.romanellas.macchinino

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothSocket
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.github.dhaval2404.colorpicker.ColorPickerDialog
import com.github.dhaval2404.colorpicker.model.ColorShape
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
        setContentView(R.layout.activity_command)

        deviceName = intent.getStringExtra("device_name") ?: "Unknown"
        deviceAddress = intent.getStringExtra("device_address") ?: ""

        if (deviceAddress.isEmpty()) {
            Toast.makeText(this, "No device address provided", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        val tv = findViewById<TextView>(R.id.statusTextView)


        val stopButton = findViewById<ImageButton>(R.id.stop)
        val leftButton = findViewById<ImageButton>(R.id.left)
        val rightButton = findViewById<ImageButton>(R.id.right)
        val upButton = findViewById<ImageButton>(R.id.up)
        val downButton = findViewById<ImageButton>(R.id.down)
        val turnLeftButton = findViewById<ImageButton>(R.id.left_indicator)
        val turnRightButton = findViewById<ImageButton>(R.id.right_indicator)
        val highlightButton = findViewById<ImageButton>(R.id.hight_lights)
        val turnOffButton = findViewById<Button>(R.id.turn_off_button)

        tv.text = "Connecting to $deviceName ($deviceAddress)..."

        thread {
            connectToDevice(tv)
        }

        stopButton.setOnClickListener { sendString("MOVE_STOP") }
        leftButton.setOnClickListener { sendString("MOVE_LEFT") }
        rightButton.setOnClickListener { sendString("MOVE_RIGHT") }
        upButton.setOnClickListener { sendString("MOVE_AHEAD") }
        downButton.setOnClickListener{ sendString("MOVE_BACK") }
        turnLeftButton.setOnClickListener { sendString("TOGGLE_TR_LF") }
        turnRightButton.setOnClickListener { sendString("TOGGLE_TR_RG") }
        highlightButton.setOnClickListener { sendString("TOGGLE_HIGH_LIGHTS") }
        turnOffButton.setOnClickListener { sendString("SYSTEM_SHUTDOWN") }

        val colorPickerBtn = findViewById<Button>(R.id.color_picker_button)
        colorPickerBtn.setOnClickListener {
            ColorPickerDialog
                .Builder(this)        				// Pass Activity Instance
                .setTitle("Pick lights")           	        // Default "Choose Color"
                .setColorShape(ColorShape.SQAURE)           // Default ColorShape.CIRCLE
                .setColorListener { color, colorHex ->
                    val (r, g, b) = hexToRgb(colorHex)
                    sendString("LIGHTS_" + r + "_" + g + "_" + b)
                }
                .show()
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

    fun hexToRgb(hex: String): Triple<Int, Int, Int> {
        val cleaned = hex.removePrefix("#")

        if (cleaned.length != 6) throw IllegalArgumentException("Hex color must be in format #RRGGBB")

        val r = cleaned.substring(0, 2).toInt(16)
        val g = cleaned.substring(2, 4).toInt(16)
        val b = cleaned.substring(4, 6).toInt(16)

        return Triple(r, g, b)
    }


}